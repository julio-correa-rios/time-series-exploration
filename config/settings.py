import os

BUFFER_SIZE = 300
DRIFT_THRESHOLD = 80
DATA_FREQUENCY = "5min"

# Redpanda docker-compose exposes Kafka on localhost:19092 (external listener).
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:19092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "grid-readings")
KAFKA_PRODUCER_DELAY = float(os.getenv("KAFKA_PRODUCER_DELAY", "0.0"))
KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "forecast-pipeline-dev")
KAFKA_AUTO_OFFSET_RESET = os.getenv("KAFKA_AUTO_OFFSET_RESET", "earliest")
KAFKA_MESSAGE_KEY = os.getenv("KAFKA_MESSAGE_KEY", "zone-1")
