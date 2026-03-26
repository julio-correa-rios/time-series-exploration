from features.pipeline import create_features


def predict(model, df):
    
    X, _ = create_features(df)
    latest = X.iloc[-1:]
    prediction = model.predict(latest)
    return prediction[0]