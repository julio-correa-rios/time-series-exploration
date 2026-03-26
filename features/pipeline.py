from features.registry import FeatureRegistry
from features.transformations import register_temporal_features


registry = FeatureRegistry()

register_temporal_features(registry)


def create_features(df):

    df = registry.compute(df)

    df = df.dropna()

    feature_cols = list(registry.features.keys())

    feature_cols.append("temperature")

    X = df[feature_cols]

    y = df["load"]
    df.to_parquet("storage/features/features.parquet")  
    return X, y