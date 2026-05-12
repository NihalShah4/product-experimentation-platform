"""
anomaly_detection.py

Purpose:
Detects unusual Daily Active User (DAU) patterns using
unsupervised machine learning.

Current Method:
- Isolation Forest

Why Isolation Forest?
- Works well for anomaly detection without labeled data
- Efficient on small-to-medium analytical datasets
- Appropriate for detecting unexpected DAU spikes/drops
- Commonly used in operational monitoring systems

Business Use Case:
This module helps identify:
- sudden traffic drops
- abnormal engagement spikes
- instrumentation failures
- campaign-driven traffic anomalies
- operational instability
"""

import pandas as pd
from sklearn.ensemble import IsolationForest

from src.metrics import get_daily_active_users


# =========================================================
# DAILY ACTIVE USER ANOMALY DETECTION
# =========================================================

def detect_dau_anomalies():
    """
    Detects anomalous DAU observations using Isolation Forest.

    Returns:
        pandas.DataFrame:
            event_date
            dau
            anomaly
            is_anomaly
    """

    # =====================================================
    # LOAD DAILY ACTIVE USER DATA
    # =====================================================

    df = get_daily_active_users()

    # =====================================================
    # ISOLATION FOREST CONFIGURATION
    # =====================================================
    #
    # contamination:
    # Estimated proportion of anomalies expected in the data.
    #
    # random_state:
    # Ensures reproducible anomaly detection behavior.
    #
    # The model operates only on DAU magnitude.
    # Future improvements could incorporate:
    # - rolling averages
    # - seasonality
    # - weekday effects
    # - campaign metadata

    model = IsolationForest(
        contamination=0.08,
        random_state=42
    )

    # =====================================================
    # MODEL TRAINING + PREDICTION
    # =====================================================
    #
    # Isolation Forest returns:
    # - 1  => normal observation
    # - -1 => anomaly

    df["anomaly"] = model.fit_predict(
        df[["dau"]]
    )

    # =====================================================
    # HUMAN-READABLE ANOMALY FLAG
    # =====================================================

    df["is_anomaly"] = df["anomaly"] == -1

    return df