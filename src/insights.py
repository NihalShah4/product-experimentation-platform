"""
insights.py

Purpose:
Generates executive-facing business insights from
analytics outputs across experimentation, forecasting,
segmentation, and product performance monitoring.

Design Philosophy:
This module intentionally converts raw analytical
metrics into stakeholder-readable narratives.

Why this matters:
Strong analytics systems should not only compute metrics —
they should also help decision-makers interpret outcomes.

Current Insight Categories:
- experimentation insights
- acquisition channel insights
- device performance insights
- forecasting insights

Future Enhancements:
- dynamic recommendation generation
- LLM-assisted insight summarization
- confidence scoring
- risk categorization
- prioritization logic
"""


# =========================================================
# EXPERIMENT INSIGHT GENERATION
# =========================================================

def generate_experiment_insight(
    p_value,
    lift
):
    """
    Interprets experiment statistical performance.

    Parameters:
        p_value (float):
            Statistical significance result.

        lift (float):
            Relative conversion lift between treatment
            and control.

    Returns:
        str:
            Executive-facing experiment interpretation.
    """

    # =====================================================
    # POSITIVE STATISTICALLY SIGNIFICANT RESULT
    # =====================================================

    if p_value < 0.05 and lift > 0:
        return (
            "The treatment variant demonstrates "
            "a statistically significant improvement "
            "in conversion performance."
        )

    # =====================================================
    # NEGATIVE STATISTICALLY SIGNIFICANT RESULT
    # =====================================================

    elif p_value < 0.05 and lift < 0:
        return (
            "The treatment variant shows a statistically "
            "significant negative impact on conversion."
        )

    # =====================================================
    # NON-SIGNIFICANT RESULT
    # =====================================================

    else:
        return (
            "No statistically significant difference "
            "was detected between experiment variants."
        )


# =========================================================
# ACQUISITION CHANNEL INSIGHT
# =========================================================

def generate_channel_insight(channel_df):
    """
    Identifies the strongest acquisition channel
    by conversion performance.

    Parameters:
        channel_df (pandas.DataFrame)

    Returns:
        str
    """

    best_channel = channel_df.iloc[0]

    return (
        f"Highest conversion performance is driven by "
        f"{best_channel['acquisition_channel']} traffic "
        f"with a conversion rate of "
        f"{best_channel['conversion_rate'] * 100:.2f}%."
    )


# =========================================================
# DEVICE PERFORMANCE INSIGHT
# =========================================================

def generate_device_insight(device_df):
    """
    Identifies the highest-performing device segment.

    Parameters:
        device_df (pandas.DataFrame)

    Returns:
        str
    """

    best_device = device_df.iloc[0]

    return (
        f"{best_device['device_type'].capitalize()} users "
        f"demonstrate the strongest conversion behavior "
        f"at {best_device['conversion_rate'] * 100:.2f}%."
    )


# =========================================================
# FORECASTING INSIGHT
# =========================================================

def generate_forecast_insight(forecast_df):
    """
    Summarizes projected Daily Active User trends.

    Parameters:
        forecast_df (pandas.DataFrame)

    Returns:
        str
    """

    avg_forecast = forecast_df[
        "forecasted_dau"
    ].mean()

    return (
        f"Based on the latest 7-day rolling activity pattern, "
        f"expected DAU for the next 14 days is approximately "
        f"{avg_forecast:.0f} users per day."
    )