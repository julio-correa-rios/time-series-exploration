import numpy as np
import pandas as pd
import time
import joblib
from sklearn.ensemble import GradientBoostingRegressor

def generate_grid_data(n_steps=1000):

    timestamps = pd.date_range(
        start="2024-01-01",
        periods=n_steps,
        freq="5min"
    )

    base_load = 1000
    daily_pattern = 200 * np.sin(2 * np.pi * timestamps.hour / 24)

    temperature = 20 + 10*np.sin(2*np.pi*timestamps.dayofyear/365)

    noise = np.random.normal(0, 30, n_steps)

    load = base_load + daily_pattern + 5*temperature + noise

    _df = pd.DataFrame({
        "timestamp": timestamps,
        "load": load,
        "temperature": temperature
    })

    return _df

def stream_data(_df):

    for _, row in _df.iterrows():

        yield row

        time.sleep(0.1)

def create_features(df):

    _df = df.copy()

    _df["lag_1"] = _df["load"].shift(1)
    _df["lag_12"] = _df["load"].shift(12)

    _df["rolling_mean"] = _df["load"].rolling(12).mean()

    _df["hour"] = _df["timestamp"].dt.hour
    _df["day_of_week"] = _df["timestamp"].dt.dayofweek

    _df = _df.dropna()

    features = [
        "lag_1",
        "lag_12",
        "rolling_mean",
        "temperature",
        "hour",
        "day_of_week"
    ]

    X = _df[features]
    y = _df["load"]

    return X, y

def train_model(X, y):

    model = GradientBoostingRegressor(
        n_estimators=200,
        max_depth=3
    )

    model.fit(X, y)

    return model

def save_model(model, version):

    path = f"models/model_v{version}.pkl"

    joblib.dump(model, path)

    print(f"Model saved: {path}")

def forecast(model, df):

    X, _ = create_features(df)

    latest = X.iloc[-1:]

    pred = model.predict(latest)

    return pred[0]

def check_drift(error, threshold=80):

    if error > threshold:
        return True

    return False

class ForecastPipeline:

    def __init__(self):

        self.buffer = []
        self.model = None
        self.version = 0

    def ingest(self, observation):

        self.buffer.append(observation)

    def retrain(self):

        df = pd.DataFrame(self.buffer)

        X, y = create_features(df)

        self.model = train_model(X, y)

        self.version += 1

        save_model(self.model, self.version)

    def predict(self):

        df = pd.DataFrame(self.buffer)

        return forecast(self.model, df)

    def run(self, stream):

        for observation in stream:

            self.ingest(observation)

            if len(self.buffer) < 100:
                continue

            if self.model is None:
                self.retrain()

            prediction = self.predict()

            actual = observation["load"]

            error = abs(prediction - actual)

            print(
                f"Actual: {actual:.1f} | "
                f"Forecast: {prediction:.1f} | "
                f"Error: {error:.1f}"
            )

            if check_drift(error):
                print("Drift detected → Retraining")
                self.retrain()

def main():
    data = generate_grid_data()

    stream = stream_data(data)

    pipeline = ForecastPipeline()

    pipeline.run(stream)

if __name__ == "__main__":
    main()

    