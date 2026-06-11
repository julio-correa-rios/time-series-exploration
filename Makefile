.PHONY: help mlflow-server clean-mlflow-legacy run streaming \
        kafka-up kafka-down streaming-kafka kafka-producer kafka-monitor \
        check-mlflow check-kafka check-deps kafka-workflow

MLFLOW_HOST ?= 127.0.0.1
MLFLOW_PORT ?= 5001
MLFLOW_BACKEND ?= ./mlruns
MLFLOW_ARTIFACTS ?= ./mlartifacts
KAFKA_HOST ?= localhost
KAFKA_PORT ?= 19092
PYTHON ?= python

help:
	@echo "Targets:"
	@echo "  mlflow-server         Start MLflow UI/server (host=$(MLFLOW_HOST) port=$(MLFLOW_PORT))"
	@echo "  clean-mlflow-legacy   Move ./mlruns/artifacts aside (legacy ops)"
	@echo "  check-mlflow          Fail fast if MLflow is not reachable"
	@echo "  check-kafka           Fail fast if Redpanda Kafka API is not reachable"
	@echo "  check-deps            Check MLflow + Kafka (for streaming-kafka)"
	@echo "  kafka-workflow        Print the multi-terminal Kafka demo steps"
	@echo "  streaming             Run the in-process streaming simulation (needs MLflow)"
	@echo "  streaming-kafka       Run forecasting pipeline from Kafka (needs MLflow + Redpanda)"
	@echo "  kafka-up              Start Redpanda + Console (Kafka API on :$(KAFKA_PORT), UI on :8080)"
	@echo "  kafka-down            Stop Redpanda stack and remove volumes"
	@echo "  kafka-producer        Produce synthetic grid readings to Kafka"
	@echo "  kafka-monitor         Print load values from Kafka (second consumer group)"
	@echo "  run                   Run main.py"

mlflow-server:
	mlflow server \
	  --backend-store-uri $(MLFLOW_BACKEND) \
	  --default-artifact-root $(MLFLOW_ARTIFACTS) \
	  --host $(MLFLOW_HOST) \
	  --port $(MLFLOW_PORT)

clean-mlflow-legacy:
	@if [ -d ./mlruns/artifacts ]; then \
	  echo "Moving legacy ./mlruns/artifacts -> ./mlruns_artifacts_legacy_backup"; \
	  mv ./mlruns/artifacts ./mlruns_artifacts_legacy_backup; \
	else \
	  echo "No ./mlruns/artifacts directory found - nothing to clean."; \
	fi

check-mlflow:
	@curl -sf "http://$(MLFLOW_HOST):$(MLFLOW_PORT)/health" >/dev/null 2>&1 || \
		(echo "ERROR: MLflow is not running at http://$(MLFLOW_HOST):$(MLFLOW_PORT)" && \
		 echo "       Start it in another terminal: make mlflow-server" && \
		 exit 1)
	@echo "OK: MLflow reachable at http://$(MLFLOW_HOST):$(MLFLOW_PORT)"

check-kafka:
	@nc -z $(KAFKA_HOST) $(KAFKA_PORT) >/dev/null 2>&1 || \
		(echo "ERROR: Kafka broker is not reachable at $(KAFKA_HOST):$(KAFKA_PORT)" && \
		 echo "       Start Redpanda: make kafka-up" && \
		 exit 1)
	@echo "OK: Kafka broker reachable at $(KAFKA_HOST):$(KAFKA_PORT)"

check-deps: check-mlflow check-kafka

kafka-workflow:
	@echo "Kafka streaming demo — run each step in its own terminal:"
	@echo ""
	@echo "  Terminal 1: make mlflow-server"
	@echo "              UI: http://$(MLFLOW_HOST):$(MLFLOW_PORT)"
	@echo "  Terminal 2: make kafka-up"
	@echo "              Console: http://localhost:8080 (create topic grid-readings)"
	@echo "  Terminal 3: make kafka-producer"
	@echo "  Terminal 4: make streaming-kafka"
	@echo ""
	@echo "Preflight only: make check-deps"

streaming: check-mlflow
	$(PYTHON) run_streaming.py

streaming-kafka: check-deps
	$(PYTHON) run_streaming_kafka.py

kafka-up:
	docker compose up -d
	@echo "Redpanda Console: http://localhost:8080"
	@echo "Kafka bootstrap:  $(KAFKA_HOST):$(KAFKA_PORT)"

kafka-down:
	docker compose down -v

kafka-producer: check-kafka
	$(PYTHON) run_kafka_producer.py

kafka-monitor: check-kafka
	$(PYTHON) run_kafka_monitor.py

run:
	$(PYTHON) main.py
