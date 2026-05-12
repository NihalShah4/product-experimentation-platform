def generate_experiment_insight(
    p_value,
    lift
):

    if p_value < 0.05 and lift > 0:
        return (
            "The treatment variant demonstrates "
            "a statistically significant improvement "
            "in conversion performance."
        )

    elif p_value < 0.05 and lift < 0:
        return (
            "The treatment variant shows a statistically "
            "significant negative impact on conversion."
        )

    else:
        return (
            "No statistically significant difference "
            "was detected between experiment variants."
        )


def generate_channel_insight(channel_df):

    best_channel = channel_df.iloc[0]

    return (
        f"Highest conversion performance is driven by "
        f"{best_channel['acquisition_channel']} traffic "
        f"with a conversion rate of "
        f"{best_channel['conversion_rate'] * 100:.2f}%."
    )


def generate_device_insight(device_df):

    best_device = device_df.iloc[0]

    return (
        f"{best_device['device_type'].capitalize()} users "
        f"demonstrate the strongest conversion behavior "
        f"at {best_device['conversion_rate'] * 100:.2f}%."
    )

def generate_forecast_insight(forecast_df):

    avg_forecast = forecast_df["forecasted_dau"].mean()

    return (
        f"Based on the latest 7-day rolling activity pattern, "
        f"expected DAU for the next 14 days is approximately "
        f"{avg_forecast:.0f} users per day."
    )