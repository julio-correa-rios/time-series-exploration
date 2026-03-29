import pandas as pd
import mlflow

from models.training import train_model
from models.inference import predict
from models.registry import ModelRegistry
from monitoring.drift import detect_drift
from config.settings import BUFFER_SIZE
from mlflow_integration import MLFlowTracker


class ForecastPipeline:
    """Time series forecasting pipeline with drift detection and MLFlow tracking."""

    def __init__(self):

        self.buffer = []
        self.model = None
        self.version = 0
        self.step = 0  # Track prediction step for MLFlow
        
        self.registry = ModelRegistry()
        
        # Initialize MLFlow tracker
        self.tracker = MLFlowTracker(experiment_name="TimeSeries-Development")
        self.active_run = None

    def ingest(self, observation):

        self.buffer.append(observation)

    def retrain(self, reason="initial"):
        """
        Retrain the model and log to MLFlow.
        
        Args:
            reason: Why retraining happened ("initial" or "drift_detected")
        """

        df = pd.DataFrame(self.buffer)

        self.model = train_model(df)

        self.version += 1

        self.registry.save(self.model, self.version)
        
        # Log retraining event to MLFlow as metric (not param, to allow multiple updates)
        if self.active_run:
            mlflow.log_metric("retrain_count", self.version, step=self.step)

    def forecast(self):

        df = pd.DataFrame(self.buffer)

        return predict(self.model, df)

    def run(self, stream):
        """
        Run the streaming pipeline with drift detection and MLFlow tracking.
        
        Args:
            stream: Iterator of observations
        """
        
        # Start MLFlow run for this streaming session
        import time
        timestamp = int(time.time())
        run_name = f"streaming_{timestamp}"
        self.active_run = self.tracker.start_run(run_name)

        for obs in stream:

            self.ingest(obs)

            if len(self.buffer) < BUFFER_SIZE:
                continue

            if self.model is None:
                self.retrain(reason="initial")

            prediction = self.forecast()

            actual = obs["load"]

            error = abs(prediction - actual)

            # Log prediction metrics to MLFlow
            self.step += 1
            mlflow.log_metric("prediction", prediction, step=self.step)
            mlflow.log_metric("actual", actual, step=self.step)
            mlflow.log_metric("error", error, step=self.step)

            print(
                f"Actual {actual:.1f} | "
                f"Pred {prediction:.1f} | "
                f"Error {error:.1f}"
            )

            if detect_drift(error):
                print("Drift detected → retraining")
                
                # Log drift event to MLFlow
                mlflow.log_metric("drift_detected", 1, step=self.step)

                self.retrain(reason="drift_detected")
        
        # End the MLFlow run
        self.tracker.end_run()