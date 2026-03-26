import pandas as pd

from models.training import train_model
from models.inference import predict
from models.registry import ModelRegistry
from monitoring.drift import detect_drift
from config.settings import BUFFER_SIZE


class ForecastPipeline:

    def __init__(self):

        self.buffer = []
        self.model = None
        self.version = 0

        self.registry = ModelRegistry()

    def ingest(self, observation):

        self.buffer.append(observation)

    def retrain(self):

        df = pd.DataFrame(self.buffer)

        self.model = train_model(df)

        self.version += 1

        self.registry.save(self.model, self.version)

    def forecast(self):

        df = pd.DataFrame(self.buffer)

        return predict(self.model, df)

    def run(self, stream):

        for obs in stream:

            self.ingest(obs)

            if len(self.buffer) < BUFFER_SIZE:
                continue

            if self.model is None:
                self.retrain()

            prediction = self.forecast()

            actual = obs["load"]

            error = abs(prediction - actual)

            print(
                f"Actual {actual:.1f} | "
                f"Pred {prediction:.1f} | "
                f"Error {error:.1f}"
            )

            if detect_drift(error):

                print("Drift detected → retraining")

                self.retrain()