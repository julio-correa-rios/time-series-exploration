import os
from typing import Optional

import mlflow

from features.registry import FeatureRegistry
from features.transformations import register_temporal_features

registry = FeatureRegistry()
register_temporal_features(registry)


def create_features(df, save_path: Optional[str] = None):
    """
    Compute model features.

    When `save_path` is provided, the engineered dataframe is written to that
    path as parquet (a transient staging file) and, if an MLflow run is
    currently active, also logged via `mlflow.log_artifact` under
    `artifact_path="features"` so each simulation owns its own copy.

    Args:
        df: Raw observations dataframe.
        save_path: Optional parquet path. When None (e.g. inference path), no
            file is written and no MLflow artifact is logged.

    Returns:
        Tuple `(X, y)` of features and target.
    """
    df = registry.compute(df)
    df = df.dropna()

    feature_cols = list(registry.features.keys())
    feature_cols.append("temperature")

    X = df[feature_cols]
    y = df["load"]

    if save_path:
        parent = os.path.dirname(save_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        df.to_parquet(save_path)
        if mlflow.active_run() is not None:
            try:
                mlflow.log_artifact(save_path, artifact_path="features")
            except Exception as exc:
                print(f"Skipped logging features artifact: {exc}")

    return X, y
