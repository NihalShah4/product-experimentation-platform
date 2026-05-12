"""
forecasting.py

Purpose:
Provides lightweight Daily Active User (DAU) forecasting
for operational monitoring and executive planning.

Current Forecasting Strategy:
- 7-day rolling average projection

Why this approach?
- fast
- explainable
- stable for synthetic analytics environments
- appropriate for baseline operational forecasting

Business Use Cases:
- short-term traffic monitoring
- retention trend visibility
- capacity planning
- experiment impact estimation
- executive KPI tracking

Future Improvements:
- ARIMA / SARIMA
- Prophet
- XGBoost forecasting
- seasonality decomposition
- holiday/event-aware forecasting
"""

import pandas as pd

from src.metrics import get_daily_active_users


# =========================================================
# DAILY ACTIVE USER FORECASTING
# =========================================================

def forecast_dau(days_ahead=14):
    """
    Generates a simple DAU forecast using a rolling average.

    Parameters:
        days_ahead (int):
            Number of future days to forecast.

    Returns:
        tuple:
            historical_dau_df,
            forecast_df
    """

    # =====================================================
    # LOAD HISTORICAL DAILY ACTIVE USERS
    # =====================================================

    df = get_daily_active_users().copy()

    df["event_date"] = pd.to_datetime(
        df["event_date"]
    )

    df = df.sort_values(
        "event_date"
    )

    # =====================================================
    # ROLLING AVERAGE FORECAST MODEL
    # =====================================================
    #
    # A 7-day rolling mean is used to smooth:
    # - day-to-day volatility
    # - synthetic randomness
    # - short-term spikes
    #
    # This creates a stable operational baseline.
    #
    # The latest rolling average value is projected
    # forward across the forecast horizon.

    rolling_mean = (
        df["dau"]
        .rolling(window=7)
        .mean()
        .iloc[-1]
    )

    # =====================================================
    # FUTURE DATE GENERATION
    # =====================================================

    future_dates = pd.date_range(
        start=(
            df["event_date"].max()
            + pd.Timedelta(days=1)
        ),
        periods=days_ahead
    )

    # =====================================================
    # FORECAST DATAFRAME
    # =====================================================

    forecast_df = pd.DataFrame({
        "event_date": future_dates,

        # Flat projection using rolling baseline
        "forecasted_dau": [
            rolling_mean
        ] * days_ahead
    })

    return df, forecast_df