"""Entry point: generate data, stream it, and run the forecasting pipeline."""

import sys

from data_simulation.generator import generate_grid_data
from data_simulation.stream import stream_data
from pipeline.forecasting_pipeline import ForecastPipeline


def main():
    data = generate_grid_data()
    stream = stream_data(data)

    pipeline = ForecastPipeline()

    try:
        pipeline.run(stream)
    except KeyboardInterrupt:
        print("Streaming interrupted by user. Exiting.")
        sys.exit(130)


if __name__ == "__main__":
    main()
