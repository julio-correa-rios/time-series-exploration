.PHONY: help mlflow-server clean-mlflow-legacy run streaming

MLFLOW_HOST ?= 127.0.0.1
MLFLOW_PORT ?= 5001
MLFLOW_BACKEND ?= ./mlruns
MLFLOW_ARTIFACTS ?= ./mlartifacts

help:
	@echo "Targets:"
	@echo "  mlflow-server         Start MLflow UI/server (host=$(MLFLOW_HOST) port=$(MLFLOW_PORT))"
	@echo "  clean-mlflow-legacy   Move ./mlruns/artifacts aside (legacy ops)"
	@echo "  streaming             Run the streaming simulation"
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

streaming:
	python run_streaming.py

run:
	python main.py
