import os
from typing import Optional

from features.registry import FeatureRegistry
from features.transformations import register_temporal_features

registry = FeatureRegistry()
register_temporal_features(registry)


def create_features(df, save_path: Optional[str] = None):
    """
    Compute model features.

    When `save_path` is provided, the engineered dataframe is written to that
    path as parquet (a transient local staging file). Uploading the parquet
    to MLflow is intentionally NOT done here on every call: in a streaming
    pipeline this would re-upload a growing file on every retrain. The
    pipeline runner takes a single final snapshot at end-of-run.

    Args:
        df: Raw observations dataframe.
        save_path: Optional parquet path. When None (e.g. inference path), no
            file is written.

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

    return X, y
