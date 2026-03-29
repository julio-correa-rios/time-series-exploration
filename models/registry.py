"""Model registry management - Local storage and MLFlow registration."""

import os
import joblib
import mlflow
from config.settings import MODEL_PATH
from mlflow_integration.config import MLFLOW_TRACKING_URI


class ModelRegistry:
    """Local model storage registry."""

    def __init__(self):
        os.makedirs(MODEL_PATH, exist_ok=True)

    def save(self, model, version):
        """Save model to disk."""
        path = f"{MODEL_PATH}/model_v{version}.pkl"
        joblib.dump(model, path)
        print("Saved model:", path)

    def load(self, version):
        """Load model from disk."""
        path = f"{MODEL_PATH}/model_v{version}.pkl"
        return joblib.load(path)


def register_best_model(experiment_name: str, model_name: str):
    """
    Register the best model from an experiment to MLFlow Model Registry.
    
    Args:
        experiment_name: Name of the experiment
        model_name: Name for the registered model
    """
    
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    
    # Get the experiment
    experiment = mlflow.get_experiment_by_name(experiment_name)
    
    if experiment is None:
        print(f"❌ Experiment '{experiment_name}' not found!")
        return
    
    # Get all runs, sorted by MAE (best first)
    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["metrics.mae ASC"]
    )
    
    if runs.empty:
        print("No runs found!")
        return
    
    # Get best run (lowest MAE)
    best_run = runs.iloc[0]
    best_run_id = best_run.run_id
    
    print(f"🏆 Best run: {best_run_id}")
    print(f"   MAE: {best_run['metrics.mae']:.4f}")
    print(f"   RMSE: {best_run['metrics.rmse']:.4f}")
    
    # Register the model from best run
    model_uri = f"runs://{best_run_id}/model"
    
    try:
        # Try to register as new version if model exists
        registered_model = mlflow.register_model(model_uri, model_name)
        print(f"✅ Registered {model_name} version {registered_model.version}")
    except Exception as e:
        print(f"⚠️ Could not register: {str(e)}")
        print("Try registering manually from MLFlow UI")


if __name__ == "__main__":
    register_best_model(
        experiment_name="TimeSeries-Development",
        model_name="TimeSeries-GradientBoosting"
    )