"""Produce synthetic grid readings to a Kafka-compatible topic (Redpanda)."""

import json
import sys
import time

from confluent_kafka import Producer

from config.settings import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_MESSAGE_KEY,
    KAFKA_PRODUCER_DELAY,
    KAFKA_TOPIC,
)
from data_simulation.generator import generate_grid_data


def _delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}", file=sys.stderr)


def _serialize_row(row) -> bytes:
    payload = {
        "timestamp": row["timestamp"].isoformat(),
        "load": float(row["load"]),
        "temperature": float(row["temperature"]),
    }
    return json.dumps(payload).encode("utf-8")


def main():
    print(
        f"Producing to topic={KAFKA_TOPIC!r} "
        f"bootstrap={KAFKA_BOOTSTRAP_SERVERS!r} "
        f"delay={KAFKA_PRODUCER_DELAY}s"
    )

    producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})
    data = generate_grid_data()
    sent = 0

    try:
        for _, row in data.iterrows():
            producer.produce(
                KAFKA_TOPIC,
                key=KAFKA_MESSAGE_KEY.encode("utf-8"),
                value=_serialize_row(row),
                callback=_delivery_report,
            )
            producer.poll(0)
            sent += 1

            if KAFKA_PRODUCER_DELAY > 0:
                time.sleep(KAFKA_PRODUCER_DELAY)
        producer.produce(
            KAFKA_TOPIC,
            key=KAFKA_MESSAGE_KEY.encode("utf-8"),
            value=json.dumps({"event": "stream_end"}).encode("utf-8"),
            callback=_delivery_report,
        )
    except KeyboardInterrupt:
        print("\nProducer interrupted. Flushing in-flight messages...")
    finally:
        producer.flush()

    print(f"Done. Produced {sent} readings to {KAFKA_TOPIC!r}.")


if __name__ == "__main__":
    main()
