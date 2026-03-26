import numpy as np


def register_temporal_features(registry):

    registry.register(
        "lag_1",
        lambda df: df["load"].shift(1)
    )

    registry.register(
        "lag_12",
        lambda df: df["load"].shift(12)
    )

    registry.register(
        "rolling_mean",
        lambda df: df["load"].rolling(12).mean()
    )

    registry.register(
        "hour_sin",
        lambda df: np.sin(
            2*np.pi*df["timestamp"].dt.hour/24
        )
    )

    registry.register(
        "hour_cos",
        lambda df: np.cos(
            2*np.pi*df["timestamp"].dt.hour/24
        )
    )

    registry.register(
        "dow_sin",
        lambda df: np.sin(
            2*np.pi*df["timestamp"].dt.dayofweek/7
        )
    )

    registry.register(
        "dow_cos",
        lambda df: np.cos(
            2*np.pi*df["timestamp"].dt.dayofweek/7
        )
    )