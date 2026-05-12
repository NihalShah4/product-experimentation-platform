import pandas as pd

from src.metrics import get_daily_active_users


def forecast_dau(days_ahead=14):

    df = get_daily_active_users().copy()

    df["event_date"] = pd.to_datetime(df["event_date"])

    df = df.sort_values("event_date")

    rolling_mean = (
        df["dau"]
        .rolling(window=7)
        .mean()
        .iloc[-1]
    )

    future_dates = pd.date_range(
        start=df["event_date"].max() + pd.Timedelta(days=1),
        periods=days_ahead
    )

    forecast_df = pd.DataFrame({
        "event_date": future_dates,
        "forecasted_dau": [rolling_mean] * days_ahead
    })

    return df, forecast_df