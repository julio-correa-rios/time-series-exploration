"""Model training with MLflow tracking."""

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


def train_model(df, run_name=None, version=None):
    """
    Train a model with MLflow tracking.

    When called inside an active MLflow run (e.g. from the streaming pipeline),
    the model is logged at artifact_path=`model_v{version}` so retrains in the
    same parent run never overwrite each other. When called standalone, a new
    MLflow run is created and the model is logged at artifact_path=`model`.

    Args:
        df: Input dataframe.
        run_name: Optional run name when starting a fresh run.
        version: Retrain version. When provided, used to namespace the model
            artifact path and step the per-retrain mae/rmse metrics.

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

        artifact_path = f"model_v{version}" if version is not None else "model"
        signature = infer_signature(X, predictions)
        input_example = X.iloc[:5]

        mlflow.sklearn.log_model(
            model,
            artifact_path=artifact_path,
            serialization_format="pickle",
            signature=signature,
            input_example=input_example,
        )

    return model
