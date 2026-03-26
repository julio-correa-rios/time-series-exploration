import numpy as np
import pandas as pd


def generate_grid_data(n_steps=2000):

    timestamps = pd.date_range(
        start="2024-01-01",
        periods=n_steps,
        freq="5min"
    )

    base_load = 1000

    daily_cycle = 200 * np.sin(
        2 * np.pi * timestamps.hour / 24
    )

    temperature = 20 + 10 * np.sin(
        2 * np.pi * timestamps.dayofyear / 365
    )

    noise = np.random.normal(0, 30, n_steps)

    load = base_load + daily_cycle + 4 * temperature + noise

    df = pd.DataFrame({
        "timestamp": timestamps,
        "load": load,
        "temperature": temperature
    })

    return df