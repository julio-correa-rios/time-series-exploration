"""MLFlow configuration module."""

import os
from dotenv import load_dotenv

load_dotenv()

# URLs and config
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MLFLOW_BACKEND_STORE_URI = os.getenv("MLFLOW_BACKEND_STORE_URI", "./mlruns")
MLFLOW_ARTIFACT_ROOT = os.getenv("MLFLOW_ARTIFACT_ROOT", "./mlartifacts")

# Experiments
EXPERIMENT_NAME = os.getenv("EXPERIMENT_NAME", "TimeSeries-Development")
RUN_NAME_PREFIX = os.getenv("RUN_NAME_PREFIX", "training")

# Default tags for all runs
DEFAULT_TAGS = {
    "environment": os.getenv("ENVIRONMENT", "development"),
    "project": "time-series-analysis",
}