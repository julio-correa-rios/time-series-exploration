"""Model training with MLflow tracking."""

import tempfile
import time
from contextlib import nullcontext

import mlflow
import mlflow.sklearn
import numpy as np
from mlflow.exceptions import MlflowException
from mlflow.models.signature import infer_signature
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from features.pipeline import create_features
from mlflow_integration import MLFlowTracker
from mlflow_integration.tracking import MLFlowRun

tracker = MLFlowTracker(experiment_name="TimeSeries-Development")

FEATURES_PARQUET = "storage/features/features.parquet"

# Explicit pip requirements for the logged model.
#
# Why this is set explicitly:
#   When `pip_requirements` is None (the default), MLflow spawns a child
#   Python subprocess on every `log_model` call to introspect imports and
#   infer the environment (~1.3s baseline). In long-running streaming runs
#   the cost of that subprocess grows with the parent's memory (fork has
#   to copy-on-write more pages), so by the 15th-20th retrain a single
#   log_model can take 15+ seconds, which is what was making the pipeline
#   feel "frozen" after roughly a dozen drift events.
#
# Listing the runtime deps here makes log_model O(50ms) and constant.
# Versions are intentionally unpinned so the captured env tracks whatever
# is installed in this venv; tighten later if reproducibility matters.
_LOG_MODEL_PIP_REQUIREMENTS = [
    "scikit-learn",
    "numpy",
    "pandas",
    "mlflow",
]


def train_model(df, run_name=None, version=None):
    """
    Train a model with MLflow tracking.

    When called inside an active MLflow run (e.g. from the streaming pipeline),
    the model is logged as a named logged-model `model_v{version}` so retrains
    in the same parent run never overwrite each other. When called standalone,
    a new MLflow run is created and the model is logged as `model`.

    Args:
        df: Input dataframe.
        run_name: Optional run name when starting a fresh run.
        version: Retrain version. When provided, used to namespace the model
            and step the per-retrain mae/rmse metrics.

    Returns:
        Trained sklearn model.
    """
    active_run = mlflow.active_run()
    is_nested = active_run is not None

    if not is_nested:
        if run_name is None:
            run_name = f"training_{int(time.time())}"
        context_manager = MLFlowRun(tracker, run_name=run_name)
    else:
        context_manager = nullcontext()

    with context_manager:
        X, y = create_features(df, save_path=FEATURES_PARQUET)

        params = {
            "n_estimators": 100,
            "max_depth": 5,
            "learning_rate": 0.1,
        }
        try:
            mlflow.log_params(params)
        except MlflowException:
            # Streaming retrains call into the same parent run; identical params
            # are fine, but mlflow rejects re-logging if values ever differ.
            pass

        model = GradientBoostingRegressor(**params)
        model.fit(X, y)

        predictions = model.predict(X)
        mae = mean_absolute_error(y, predictions)
        rmse = np.sqrt(mean_squared_error(y, predictions))

        step = version if version is not None else 0
        mlflow.log_metric("mae", mae, step=step)
        mlflow.log_metric("rmse", rmse, step=step)

        model_name = f"model_v{version}" if version is not None else "model"
        signature = infer_signature(X, predictions)
        input_example = X.iloc[:5]

        # We deliberately avoid `mlflow.sklearn.log_model(...)` here.
        #
        # In MLflow 3, `log_model` creates a "Logged Model" entity and calls
        # `log_model_metrics_for_step`, which fetches the run's *entire* metric
        # history and re-attaches it to the new model on every call. In a long
        # streaming run that means each retrain becomes O(N) in the number of
        # accumulated metric points, and `log_model` time roughly doubles per
        # drift event - going from ~0.1s early on to >25s by the 19th retrain.
        #
        # `save_model` writes the same MLflow model package to a local path,
        # and `log_artifacts` uploads it under a per-version artifact path.
        # The run still gets a full, loadable model artifact tree per retrain
        # (visible in the UI under `artifacts/model_v{N}/`), but without the
        # quadratic metric-correlation work.
        with tempfile.TemporaryDirectory() as tmp_dir:
            model_path = f"{tmp_dir}/model"
            mlflow.sklearn.save_model(
                model,
                path=model_path,
                serialization_format="pickle",
                signature=signature,
                input_example=input_example,
                pip_requirements=_LOG_MODEL_PIP_REQUIREMENTS,
            )
            mlflow.log_artifacts(model_path, artifact_path=model_name)

    return model
