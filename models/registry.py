import os
import joblib

from config.settings import MODEL_PATH


class ModelRegistry:

    def __init__(self):

        os.makedirs(MODEL_PATH, exist_ok=True)

    def save(self, model, version):

        path = f"{MODEL_PATH}/model_v{version}.pkl"

        joblib.dump(model, path)

        print("Saved model:", path)

    def load(self, version):

        path = f"{MODEL_PATH}/model_v{version}.pkl"

        return joblib.load(path)