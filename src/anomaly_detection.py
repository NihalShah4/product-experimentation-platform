import pandas as pd
from sklearn.ensemble import IsolationForest

from src.metrics import get_daily_active_users


def detect_dau_anomalies():

    df = get_daily_active_users()

    model = IsolationForest(
        contamination=0.08,
        random_state=42
    )

    df["anomaly"] = model.fit_predict(
        df[["dau"]]
    )

    df["is_anomaly"] = df["anomaly"] == -1

    return df