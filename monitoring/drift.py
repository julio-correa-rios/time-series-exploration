from config.settings import DRIFT_THRESHOLD


def detect_drift(error):

    return error > DRIFT_THRESHOLD