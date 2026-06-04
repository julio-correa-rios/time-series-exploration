"""Streaming forecast pipeline with drift detection, MLflow tracking, and graceful shutdown."""

import os
import signal
import time
from collections import deque

import mlflow
import pandas as pd

from config.settings import BUFFER_SIZE
from mlflow_integration import MLFlowTracker
from models.inference import predict
from models.training import FEATURES_PARQUET, train_model
from monitoring.drift import detect_drift


class ForecastPipeline:
    """Time series forecasting pipeline with drift detection and MLflow tracking."""

    def __init__(self):
        # Bounded rolling window: keeps memory + per-retrain cost flat as the
        # stream grows. Each retrain trains on exactly the last BUFFER_SIZE
        # observations rather than the full history.
        self.buffer: "deque" = deque(maxlen=BUFFER_SIZE)
        self.model = None
        self.version = 0
        self.step = 0

        self.tracker = MLFlowTracker(experiment_name="TimeSeries-Development")
        self.active_run = None

        self._shutdown_requested = False
        self.was_killed = False

    def ingest(self, observation):
        self.buffer.append(observation)

    def retrain(self, reason="initial"):
        """
        Retrain the model and log the new version to MLflow.

        Each retrain bumps `self.version` and the new model is logged at
        artifact_path=`model_v{version}` inside the active streaming run, so
        retrains in the same simulation never overwrite each other.
        """
        df = pd.DataFrame(self.buffer)
        self.version += 1
        self.model = train_model(df, version=self.version)

        if self.active_run is not None:
            mlflow.log_metric("retrain_count", self.version, step=self.step)
            mlflow.set_tag(f"retrain_v{self.version}_reason", reason)

    # Enough history to compute lag_12 + rolling_mean(12) + one prediction row.
    _PREDICT_TAIL = 50

    def forecast(self):
        # Predicting the next step only needs a small recent tail. deque does
        # not support slice indexing, so convert to list and then slice.
        tail = list(self.buffer)[-self._PREDICT_TAIL:]
        df = pd.DataFrame(tail)
        return predict(self.model, df)

    def _install_sigint_handler(self):
        """Install a two-stage SIGINT handler. First press drains, second forces exit."""
        original = signal.getsignal(signal.SIGINT)

        def handler(signum, frame):
            if self._shutdown_requested:
                # Second Ctrl+C: restore default and let the next press kill us.
                signal.signal(signal.SIGINT, original)
                print("\nForce quit requested. Exiting now.")
                raise KeyboardInterrupt
            self._shutdown_requested = True
            print(
                "\nShutdown requested. Finishing the current step and closing the "
                "MLflow run cleanly. Press Ctrl+C again to force quit."
            )

        signal.signal(signal.SIGINT, handler)
        return original

    def run(self, stream):
        """
        Run the streaming pipeline with drift detection, MLflow tracking, and
        graceful shutdown.

        Args:
            stream: Iterator of observations (each obs has `load`, `temperature`, ...).
        """
        original_handler = self._install_sigint_handler()

        run_name = f"streaming_{int(time.time())}"
        self.active_run = self.tracker.start_run(run_name)

        final_status = "FINISHED"

        try:
            for obs in stream:
                if self._shutdown_requested:
                    final_status = "KILLED"
                    self.was_killed = True
                    break

                self.ingest(obs)

                if len(self.buffer) < BUFFER_SIZE:
                    continue

                if self.model is None:
                    self.retrain(reason="initial")

                prediction = self.forecast()
                actual = obs["load"]
                error = abs(prediction - actual)

                self.step += 1
                mlflow.log_metrics(
                    {
                        "prediction": prediction,
                        "actual": actual,
                        "error": error,
                    },
                    step=self.step,
                )

                print(
                    f"Actual {actual:.1f} | "
                    f"Pred {prediction:.1f} | "
                    f"Error {error:.1f}"
                )

                if detect_drift(error):
                    print("Drift detected -> retraining")
                    mlflow.log_metric("drift_detected", 1, step=self.step)
                    self.retrain(reason="drift_detected")
        except KeyboardInterrupt:
            final_status = "KILLED"
            self.was_killed = True
            raise
        except Exception:
            final_status = "FAILED"
            raise
        finally:
            if mlflow.active_run() is not None:
                # Log the final features parquet ONCE per run. Doing this per
                # retrain caused growing-file uploads on every drift event.
                if os.path.exists(FEATURES_PARQUET):
                    try:
                        mlflow.log_artifact(
                            FEATURES_PARQUET, artifact_path="features"
                        )
                    except Exception as exc:
                        print(f"Could not log final features artifact: {exc}")
                mlflow.end_run(status=final_status)
            signal.signal(signal.SIGINT, original_handler)
            print(
                f"\nRun ended. status={final_status} "
                f"steps={self.step} retrains={self.version}"
            )
