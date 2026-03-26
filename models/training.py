from sklearn.ensemble import GradientBoostingRegressor

from features.pipeline import create_features


def train_model(df):

    X, y = create_features(df)

    model = GradientBoostingRegressor()

    model.fit(X, y)

    return model