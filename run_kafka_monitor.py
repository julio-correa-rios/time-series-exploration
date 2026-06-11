"""Second consumer group: print load values from Kafka (Phase 5 learning exercise)."""

import json
import sys

from confluent_kafka import Consumer, KafkaError, KafkaException

from config.settings import (
    KAFKA_AUTO_OFFSET_RESET,
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC,
)

MONITOR_GROUP_ID = "grid-monitor-dev"


def main():
    print(
        f"Monitoring topic={KAFKA_TOPIC!r} group={MONITOR_GROUP_ID!r} "
        f"bootstrap={KAFKA_BOOTSTRAP_SERVERS!r}"
    )

    consumer = Consumer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "group.id": MONITOR_GROUP_ID,
            "auto.offset.reset": KAFKA_AUTO_OFFSET_RESET,
            "enable.auto.commit": True,
        }
    )
    consumer.subscribe([KAFKA_TOPIC])

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                raise KafkaException(msg.error())

            payload = json.loads(msg.value().decode("utf-8"))
            if payload.get("event") == "stream_end":
                print("stream_end received — monitor exiting.")
                break

            print(
                f"partition={msg.partition()} offset={msg.offset()} "
                f"load={payload['load']:.1f}"
            )
    except KeyboardInterrupt:
        print("\nMonitor stopped.")
        sys.exit(130)
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
