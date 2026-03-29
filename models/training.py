"""Model training with MLFlow tracking."""

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.ensemble import GradientBoostingRegressor
import mlflow
import mlflow.sklearn

from mlflow_integration import MLFlowTracker
from mlflow_integration.tracking import MLFlowRun
from features.pipeline import create_features

tracker = MLFlowTracker(experiment_name="TimeSeries-Development")

def train_model(df, run_name=None):
    """
    Train a model with MLFlow tracking.
    
    Each call to this function creates a new MLFlow run (if not nested).
    When called from within an active run, logs to that run instead.
    
    Args:
        df: Input dataframe
        run_name: Name for this training run (auto-generated if None)
        
    Returns:
        Trained model
    """
    
    # Check if there's already an active run
    active_run = mlflow.active_run()
    is_nested = active_run is not None
    
    # Only create a new run if there isn't one already
    if not is_nested:
        if run_name is None:
            import time
            timestamp = int(time.time())
            run_name = f"training_{timestamp}"
        context_manager = MLFlowRun(tracker, run_name=run_name)
    else:
        # Use a dummy context manager that doesn't create a run
        from contextlib import nullcontext
        context_manager = nullcontext()

    with context_manager:
        X, y = create_features(df)
        
        params = {
            "n_estimators": 100,
            "max_depth": 5,
            "learning_rate": 0.1,
        }
        mlflow.log_params(params)
        
        # Train model
        model = GradientBoostingRegressor(**params)
        model.fit(X, y)
        
        # Calculate and log metrics
        predictions = model.predict(X)
        mae = mean_absolute_error(y, predictions)
        rmse = np.sqrt(mean_squared_error(y, predictions))
        
        metrics = {"mae": mae, "rmse": rmse}
        mlflow.log_metrics(metrics)
        
        # Log model in pickle format
        mlflow.sklearn.log_model(
            model, 
            artifact_path="model",
            serialization_format="pickle"
        )
    
    return model

