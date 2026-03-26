# Standard library
import logging

# Third-party
import pandas as pd

# # Add paths
# import sys
# import os

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Local modules
from data_simulation.generator import generate_grid_data
from data_simulation.stream import stream_data
from pipeline.forecasting_pipeline import ForecastPipeline

def main():

    data = generate_grid_data()

    stream = stream_data(data)

    pipeline = ForecastPipeline()

    pipeline.run(stream)


if __name__ == "__main__":
    main()