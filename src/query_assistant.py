from src.metrics import (
    get_conversion_rate,
    get_funnel_conversion,
    get_conversion_by_channel,
    get_conversion_by_device
)

from src.experiment_analysis import (
    get_experiment_results,
    run_chi_square_test
)

from src.forecasting import forecast_dau


def answer_query(user_query):

    query = user_query.lower()

    if "conversion" in query and "channel" not in query and "device" not in query:
        conversion_df = get_conversion_rate()
        conversion_rate = conversion_df.iloc[0]["conversion_rate"]

        return (
            f"The overall conversion rate is "
            f"{conversion_rate * 100:.2f}%."
        )

    if "funnel" in query or "dropoff" in query:
        funnel_df = get_funnel_conversion()

        return funnel_df

    if "channel" in query:
        channel_df = get_conversion_by_channel()

        best_channel = channel_df.iloc[0]

        return (
            f"The strongest acquisition channel is "
            f"{best_channel['acquisition_channel']} with a conversion rate of "
            f"{best_channel['conversion_rate'] * 100:.2f}%."
        )

    if "device" in query:
        device_df = get_conversion_by_device()

        best_device = device_df.iloc[0]

        return (
            f"The strongest device segment is "
            f"{best_device['device_type']} with a conversion rate of "
            f"{best_device['conversion_rate'] * 100:.2f}%."
        )

    if "experiment" in query or "ab test" in query or "a/b" in query:

        experiment_df = get_experiment_results()

        p_value = run_chi_square_test(
            experiment_df
        )

        control_rate = experiment_df[
            experiment_df["variant"] == "control"
        ]["conversion_rate"].iloc[0]

        treatment_rate = experiment_df[
            experiment_df["variant"] == "treatment"
        ]["conversion_rate"].iloc[0]

        lift = (
            (treatment_rate - control_rate)
            / control_rate
        ) * 100

        significance = (
            "statistically significant"
            if p_value < 0.05
            else "not statistically significant"
        )

        recommendation = (
            "Recommend rollout."
            if p_value < 0.05 and lift > 0
            else "Do not recommend rollout."
        )

        return (
            f"Control conversion rate: "
            f"{control_rate * 100:.2f}%\n\n"

            f"Treatment conversion rate: "
            f"{treatment_rate * 100:.2f}%\n\n"

            f"Treatment lift: "
            f"{lift:.2f}%\n\n"

            f"P-value: "
            f"{p_value:.4f}\n\n"

            f"Result: The experiment is "
            f"{significance}.\n\n"

            f"{recommendation}"
        )

    if "forecast" in query or "future" in query:
        _, forecast_df = forecast_dau()
        avg_forecast = forecast_df["forecasted_dau"].mean()

        return (
            f"The 14-day DAU forecast is approximately "
            f"{avg_forecast:.0f} users per day."
        )

    return (
        "I can answer questions about conversion rate, funnel performance, "
        "channel performance, device performance, experiments, and DAU forecasts."
    )