# Kafka / Redpanda Learning Guide

This project can stream grid-load observations through a Kafka-compatible
broker (Redpanda) instead of an in-process Python iterator.

## Concepts (mapped to this repo)

| Term | In this project |
|------|-----------------|
| **Topic** | `grid-readings` — channel for synthetic observations |
| **Partition** | Ordered sub-log; start with 1 partition for simple global ordering |
| **Offset** | Message index within a partition; consumer bookmark for replay |
| **Producer** | `run_kafka_producer.py` — emits rows from `generate_grid_data()` |
| **Consumer** | `stream_from_kafka()` → `ForecastPipeline.run()` |
| **Consumer group** | `forecast-pipeline-dev` — resume vs replay depends on group id |

## Prerequisites

- Docker Desktop (or Docker Engine + Compose plugin)
- Python deps: `pip install -e ".[kafka]"`

## Phase 1 — Broker only (manual UI check)

```bash
make kafka-up
```

Open **Redpanda Console**: http://localhost:8080

1. Create topic `grid-readings` (1 partition)
2. Produce a test JSON message:
   ```json
   {"timestamp": "2024-01-01T00:00:00", "load": 1000.0, "temperature": 20.0}
   ```
3. Consume it in the UI to confirm the broker works

Stop the broker:

```bash
make kafka-down
```

## Full workflow

Print the steps anytime:

```bash
make kafka-workflow
```

Run each step in its own terminal:

```bash
# Terminal 1 — MLflow UI
make mlflow-server

# Terminal 2 — Redpanda + Console
make kafka-up

# Terminal 3 — produce synthetic readings
make kafka-producer

# Terminal 4 — consume and run the forecasting pipeline
make streaming-kafka
```

`make streaming-kafka`, `make kafka-producer`, and `make streaming` run **preflight
checks** first. If MLflow or Redpanda is down, you get a short error instead of
a long Python traceback:

```bash
make check-deps    # verify both before starting
make check-mlflow  # MLflow only
make check-kafka   # Redpanda only
```

With uv: `make streaming-kafka PYTHON="uv run --extra kafka python"`

**Bootstrap address:** Redpanda exposes Kafka on `localhost:19092` (not 9092).
Override with `KAFKA_BOOTSTRAP_SERVERS` in `.env` if needed.

The producer sends a `stream_end` sentinel after all readings so the consumer
can finish naturally (like the in-process iterator) and register the best model.

## Learning exercises (Phase 5)

### 1. Replay

Stop the consumer, then restart with a **new** consumer group:

```bash
KAFKA_CONSUMER_GROUP=replay-test python run_streaming_kafka.py
```

With `KAFKA_AUTO_OFFSET_RESET=earliest` (default), the consumer re-reads
all messages from the beginning.

### 2. Resume

Restart with the **same** `KAFKA_CONSUMER_GROUP` — processing continues
from the last committed offset.

### 3. Pacing

Slow the producer for a visible real-time cadence:

```bash
KAFKA_PRODUCER_DELAY=0.1 python run_kafka_producer.py
```

### 4. Second consumer group

Run the monitor script in another terminal while the pipeline consumes:

```bash
python run_kafka_monitor.py
```

Same topic, independent offset cursor — classic pub/sub at the log layer.

### 5. Partitioning preview

In Console, recreate `grid-readings` with 2 partitions. Produce with
keys `zone-1` and `zone-2` (the producer already keys messages as
`zone-1`). Observe how messages distribute across partitions; ordering
is guaranteed **per partition** only.
