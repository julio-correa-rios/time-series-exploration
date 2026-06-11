"""Run the forecasting pipeline consuming observations from Kafka."""

import sys

from config.settings import (
    KAFKA_AUTO_OFFSET_RESET,
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_CONSUMER_GROUP,
    KAFKA_TOPIC,
)
from data_simulation.kafka_stream import stream_from_kafka
from models.registry import register_best_model
from pipeline.forecasting_pipeline import ForecastPipeline


def main():
    """Run streaming experiment with Kafka as the data source."""
    print(
        "Starting Kafka-backed streaming experiment...\n"
        f"  topic:    {KAFKA_TOPIC}\n"
        f"  bootstrap: {KAFKA_BOOTSTRAP_SERVERS}\n"
        f"  group:    {KAFKA_CONSUMER_GROUP}\n"
        f"  offset:   {KAFKA_AUTO_OFFSET_RESET}"
    )

    stream = stream_from_kafka(
        topic=KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_CONSUMER_GROUP,
        auto_offset_reset=KAFKA_AUTO_OFFSET_RESET,
    )

    pipeline = ForecastPipeline()

    try:
        pipeline.run(stream)
    except KeyboardInterrupt:
        print("Streaming interrupted by user. Exiting.")
        sys.exit(130)

    if pipeline.was_killed:
        print(
            "Run was killed before natural completion. "
            "Skipping best-model registration."
        )
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
