"""Register the best run's model into the MLflow Model Registry."""

import mlflow
from mlflow.tracking import MlflowClient

from mlflow_integration.config import MLFLOW_TRACKING_URI


def _latest_model_artifact_path(client: MlflowClient, run_id: str) -> str:
    """
    Find the latest `model_v{n}` artifact directory for a run, falling back to
    `model` (legacy single-model layout) when no versioned artifacts exist.
    """
    artifacts = client.list_artifacts(run_id)
    versioned = []
    for art in artifacts:
        if not art.is_dir:
            continue
        name = art.path
        if name.startswith("model_v"):
            try:
                versioned.append((int(name.split("model_v", 1)[1]), name))
            except ValueError:
                continue
    if versioned:
        versioned.sort()
        return versioned[-1][1]
    return "model"


def register_best_model(experiment_name: str, model_name: str):
    """
    Register the best model (lowest MAE) from an experiment into the MLflow
    Model Registry.

    Args:
        experiment_name: Name of the experiment to search.
        model_name: Name to register the model under.
    """
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        print(f"Experiment '{experiment_name}' not found.")
        return

    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.mae ASC"],
    )

    if runs.empty:
        print("No runs found.")
        return

    best_run = runs.iloc[0]
    best_run_id = best_run.run_id

    print(f"Best run: {best_run_id}")
    if "metrics.mae" in best_run and best_run["metrics.mae"] is not None:
        print(f"  MAE:  {best_run['metrics.mae']:.4f}")
    if "metrics.rmse" in best_run and best_run["metrics.rmse"] is not None:
        print(f"  RMSE: {best_run['metrics.rmse']:.4f}")

    client = MlflowClient()
    artifact_path = _latest_model_artifact_path(client, best_run_id)
    model_uri = f"runs:/{best_run_id}/{artifact_path}"
    print(f"  artifact: {artifact_path}")

    try:
        registered_model = mlflow.register_model(model_uri, model_name)
        print(f"Registered '{model_name}' version {registered_model.version}.")
    except Exception as e:
        print(f"Could not register model: {e}")
        print("You can register it manually from the MLflow UI.")


if __name__ == "__main__":
    register_best_model(
        experiment_name="TimeSeries-Development",
        model_name="TimeSeries-GradientBoosting",
    )
