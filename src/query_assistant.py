"""
query_assistant.py

Purpose:
Provides lightweight rule-based analytics question
handling for the Product Intelligence Platform.

Design Philosophy:
This module acts as a deterministic analytics assistant.

Unlike the LLM assistant:
- responses here are fully controlled
- metrics are computed directly from analytical functions
- no generative reasoning is involved

Why both systems exist:
1. query_assistant.py
   -> deterministic analytics lookup

2. llm_assistant.py
   -> strategic interpretation + recommendations

This mirrors real-world analytics architecture where:
- hard metrics remain deterministic
- LLMs assist with interpretation only

Supported Query Categories:
- conversion rate
- funnel analysis
- acquisition channels
- device performance
- experimentation
- forecasting
"""

from src.experiment_analysis import (
    get_experiment_results,
    run_chi_square_test
)

from src.forecasting import forecast_dau

from src.metrics import (
    get_conversion_by_channel,
    get_conversion_by_device,
    get_conversion_rate,
    get_funnel_conversion
)


# =========================================================
# RULE-BASED ANALYTICS QUERY HANDLER
# =========================================================

def answer_query(user_query):
    """
    Processes lightweight product analytics questions
    using deterministic rule-based logic.

    Parameters:
        user_query (str)

    Returns:
        str OR pandas.DataFrame
    """

    # =====================================================
    # QUERY NORMALIZATION
    # =====================================================

    query = user_query.lower()

    # =====================================================
    # OVERALL CONVERSION RATE
    # =====================================================

    if (
        "conversion" in query
        and "channel" not in query
        and "device" not in query
    ):

        conversion_df = get_conversion_rate()

        conversion_rate = conversion_df.iloc[0][
            "conversion_rate"
        ]

        return (
            f"The overall conversion rate is "
            f"{conversion_rate * 100:.2f}%."
        )

    # =====================================================
    # FUNNEL + DROPOFF ANALYSIS
    # =====================================================

    if "funnel" in query or "dropoff" in query:

        funnel_df = get_funnel_conversion()

        return funnel_df

    # =====================================================
    # ACQUISITION CHANNEL PERFORMANCE
    # =====================================================

    if "channel" in query:

        channel_df = get_conversion_by_channel()

        best_channel = channel_df.iloc[0]

        return (
            f"The strongest acquisition channel is "
            f"{best_channel['acquisition_channel']} with a conversion rate of "
            f"{best_channel['conversion_rate'] * 100:.2f}%."
        )

    # =====================================================
    # DEVICE PERFORMANCE ANALYSIS
    # =====================================================

    if "device" in query:

        device_df = get_conversion_by_device()

        best_device = device_df.iloc[0]

        return (
            f"The strongest device segment is "
            f"{best_device['device_type']} with a conversion rate of "
            f"{best_device['conversion_rate'] * 100:.2f}%."
        )

    # =====================================================
    # EXPERIMENT ANALYSIS
    # =====================================================

    if (
        "experiment" in query
        or "ab test" in query
        or "a/b" in query
    ):

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

        # =================================================
        # RELATIVE TREATMENT LIFT
        # =================================================

        lift = (
            (treatment_rate - control_rate)
            / control_rate
        ) * 100

        # =================================================
        # STATISTICAL SIGNIFICANCE INTERPRETATION
        # =================================================

        significance = (
            "statistically significant"
            if p_value < 0.05
            else "not statistically significant"
        )

        # =================================================
        # SIMPLE ROLLOUT RECOMMENDATION
        # =================================================

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

    # =====================================================
    # DAU FORECASTING
    # =====================================================

    if "forecast" in query or "future" in query:

        _, forecast_df = forecast_dau()

        avg_forecast = forecast_df[
            "forecasted_dau"
        ].mean()

        return (
            f"The 14-day DAU forecast is approximately "
            f"{avg_forecast:.0f} users per day."
        )

    # =====================================================
    # FALLBACK RESPONSE
    # =====================================================

    return (
        "I can answer questions about conversion rate, "
        "funnel performance, channel performance, "
        "device performance, experiments, and DAU forecasts."
    )