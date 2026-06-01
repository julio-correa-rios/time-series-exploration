"""Synthetic streaming generator used to feed the forecasting pipeline."""

import time


def stream_data(df, delay: float = 0.0):
    """
    Yield rows one at a time, optionally pacing for demo purposes.

    Args:
        df: Source dataframe to iterate.
        delay: Seconds to sleep between rows. Defaults to 0.0 (no pacing).
            Set this when you want a visible real-time cadence; leave at 0
            for batch experiments and benchmarks.
    """
    for _, row in df.iterrows():
        yield row
        if delay > 0:
            time.sleep(delay)
