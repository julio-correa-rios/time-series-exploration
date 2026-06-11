"""Kafka-backed stream adapter — yields observations compatible with ForecastPipeline."""

import json
from typing import Iterator

import pandas as pd
from confluent_kafka import Consumer, KafkaError, KafkaException


def _is_stream_end(value: bytes) -> bool:
    payload = json.loads(value.decode("utf-8"))
    return payload.get("event") == "stream_end"


def _parse_message(value: bytes) -> dict:
    """Deserialize a JSON grid-reading payload into a pipeline observation."""
    payload = json.loads(value.decode("utf-8"))
    return {
        "timestamp": pd.Timestamp(payload["timestamp"]),
        "load": float(payload["load"]),
        "temperature": float(payload["temperature"]),
    }


def stream_from_kafka(
    topic: str,
    bootstrap_servers: str,
    group_id: str,
    auto_offset_reset: str = "earliest",
    poll_timeout_sec: float = 1.0,
) -> Iterator[dict]:
    """
    Poll a Kafka topic and yield observations one at a time.

    Each yielded dict matches the shape produced by generate_grid_data() /
    stream_data(): timestamp, load, temperature. ForecastPipeline.run() can
    consume this iterator without modification.

    The consumer is closed when the iterator is exhausted or when the caller
    breaks out of the loop (generator.close() triggers the finally block).
    """
    consumer = Consumer(
        {
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": auto_offset_reset,
            "enable.auto.commit": True,
        }
    )
    consumer.subscribe([topic])

    try:
        while True:
            msg = consumer.poll(poll_timeout_sec)
            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                raise KafkaException(msg.error())

            if _is_stream_end(msg.value()):
                break

            yield _parse_message(msg.value())
    finally:
        consumer.close()
