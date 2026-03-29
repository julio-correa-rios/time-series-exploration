"""MLFlow tracking wrapper for experiment and model logging."""

import mlflow
from mlflow.sklearn import log_model
from typing import Dict, Any, Optional
from mlflow_integration.config import (
    MLFLOW_TRACKING_URI,
    MLFLOW_BACKEND_STORE_URI,
    EXPERIMENT_NAME,
    DEFAULT_TAGS,
)


class MLFlowTracker:
    """Simplified MLFlow tracker."""
    
    def __init__(self, experiment_name: str = EXPERIMENT_NAME):
        """
        Initialise the MLFlow tracker.
        
        Args:
            experiment_name: Name of the experiment in MLFlow
        """
        # URI Config 
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        
        # Get the experiment ID, create if it doesn't exist
        self.experiment_name = experiment_name
        try:
            experiment_id = mlflow.create_experiment(
                experiment_name,
                artifact_location=None
            )
            self.experiment_id = experiment_id
        except:
            # If the experiment already exists, get its ID
            experiment = mlflow.get_experiment_by_name(experiment_name)
            self.experiment_id = experiment.experiment_id
        
        # Stablish the experiment as an active experiment
        mlflow.set_experiment(experiment_name)
    
    def start_run(self, run_name: str, tags: Optional[Dict[str, str]] = None):
        """
        Start a new MLFlow run.
        
        Args:
            run_name: Descriptive name for the run
            tags: Dictionary of additional tags
        """
        # Combine default tags with custom tags
        all_tags = {**DEFAULT_TAGS}
        if tags:
            all_tags.update(tags)
        
        # Start the run
        mlflow.start_run(run_name=run_name, tags=all_tags)
        return mlflow.active_run()
    
    def end_run(self):
        """End the current run."""
        mlflow.end_run()
    
    def log_params(self, params: Dict[str, Any]):
        """
        Log model parameters.
        
        Args:
            params: Dictionary of parameters (e.g., hyperparameters)
        """
        mlflow.log_params(params)
    
    def log_metrics(self, metrics: Dict[str, float]):
        """
        Log evaluation metrics.
        
        Args:
            metrics: Dictionary of metrics (e.g., MAE, RMSE)
        """
        mlflow.log_metrics(metrics)
    
    def log_model(self, model, model_name: str = "model"):
        """
        Log the trained model.
        
        Args:
            model: Trained model (sklearn compatible)
            model_name: Name of the model in the artifact store
        """
        log_model(model, model_name)
    
    def log_metric_step(self, metric_name: str, value: float, step: int):
        """
        Log a metric with step (for time series).
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            step: Step/epoch number
        """
        mlflow.log_metric(metric_name, value, step=step)


# Context manager for using with 'with' statement
class MLFlowRun:
    """Context manager for MLFlow runs."""
    
    def __init__(self, tracker: MLFlowTracker, run_name: str, tags: Optional[Dict] = None):
        self.tracker = tracker
        self.run_name = run_name
        self.tags = tags
    
    def __enter__(self):
        self.tracker.start_run(self.run_name, self.tags)
        return self.tracker
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tracker.end_run()