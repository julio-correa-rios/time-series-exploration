"""Run the full streaming pipeline with MLflow tracking."""

import sys

from data_simulation.generator import generate_grid_data
from data_simulation.stream import stream_data
from models.registry import register_best_model
from pipeline.forecasting_pipeline import ForecastPipeline


def main():
    """Run streaming experiment with drift detection."""
    print("Starting streaming experiment with drift detection...")

    data = generate_grid_data()
    stream = stream_data(data)

    pipeline = ForecastPipeline()

    try:
        pipeline.run(stream)
    except KeyboardInterrupt:
        print("Streaming interrupted by user. Exiting.")
        sys.exit(130)

    if pipeline.was_killed:
        print("Run was killed before natural completion. "
              "Skipping best-model registration.")
        sys.exit(130)

    print("Streaming completed.")
    print(f"  Total steps: {pipeline.step}")
    print(f"  Retrains:    {pipeline.version}")

    print("\nRegistering best model...")
    register_best_model(
        experiment_name="TimeSeries-Development",
        model_name="TimeSeries-GradientBoosting",
    )

    print("Done. Check the MLflow UI: http://localhost:5001")


if __name__ == "__main__":
    main()
