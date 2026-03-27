"""Model training with MLFlow tracking."""

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.ensemble import GradientBoostingRegressor
import mlflow.sklearn

from mlflow_integration import MLFlowTracker
from mlflow_integration.tracking import MLFlowRun
from features.pipeline import create_features

tracker = MLFlowTracker(experiment_name="TimeSeries-Development")

def train_model(df, run_name="training_v1"):
    """
    Train a model with MLFlow tracking.
    
    Each call to this function creates a new MLFlow run.
    Multiple calls happen when drift is detected in the pipeline.
    
    Args:
        df: Input dataframe
        run_name: Name for this training run
        
    Returns:
        Trained model
    """
    
    # Use context manager for clean run handling
    with MLFlowRun(tracker, run_name=run_name):
        X, y = create_features(df)
        
        params = {
            "n_estimators": 100,
            "max_depth": 5,
            "learning_rate": 0.1,
        }
        tracker.log_params(params)
        
        # Train model
        model = GradientBoostingRegressor(**params)
        model.fit(X, y)
        
        # Calculate and log metrics
        predictions = model.predict(X)
        mae = mean_absolute_error(y, predictions)
        rmse = np.sqrt(mean_squared_error(y, predictions))
        
        metrics = {"mae": mae, "rmse": rmse}
        tracker.log_metrics(metrics)
        
        # Log model in pickle format
        mlflow.sklearn.log_model(
            model, 
            artifact_path="model",
            serialization_format="pickle"
        )
    
        # New to register the model in the MLFlow Model Registry:
        import mlflow
        model_uri = f"runs://{mlflow.active_run().info.run_id}/model"
        mlflow.register_model(model_uri, "TimeSeries-GradientBoosting")

    return model

