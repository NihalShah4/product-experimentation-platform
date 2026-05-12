import streamlit as st
import pandas as pd
import plotly.express as px

from src.experiment_analysis import (
    get_experiment_results,
    run_chi_square_test
)

from src.retention_analysis import (
    get_retention_data
)

from src.metrics import (
    get_daily_active_users,
    get_conversion_rate,
    get_funnel_metrics,
    get_conversion_by_channel,
    get_conversion_by_device,
    get_funnel_conversion,
    engine
)

from src.insights import (
    generate_experiment_insight,
    generate_channel_insight,
    generate_device_insight,
    generate_forecast_insight
)

from src.anomaly_detection import detect_dau_anomalies
from src.forecasting import forecast_dau
from src.query_assistant import answer_query
from src.llm_assistant import generate_llm_response


st.set_page_config(
    page_title="Product Experimentation Platform",
    layout="wide"
)

st.title("Product Experimentation Platform")

st.write(
    "Google-style product analytics and experimentation dashboard."
)

st.sidebar.title("Analytics Controls")

selected_variant = st.sidebar.selectbox(
    "Experiment Variant",
    ["All", "control", "treatment"]
)


def get_variant_condition(alias="e"):
    if selected_variant == "All":
        return ""
    return f"AND {alias}.variant = '{selected_variant}'"


def get_filtered_dau():
    variant_condition = get_variant_condition("e")

    query = f"""
    SELECT
        e.event_date,
        COUNT(DISTINCT e.user_id) AS dau
    FROM events e
    WHERE 1 = 1
        {variant_condition}
    GROUP BY e.event_date
    ORDER BY e.event_date
    """

    return pd.read_sql(query, engine)


def get_filtered_conversion_rate():
    variant_condition = get_variant_condition("e")

    query = f"""
    WITH sessions AS (
        SELECT DISTINCT e.session_id
        FROM events e
        WHERE e.event_type = 'session_start'
            {variant_condition}
    ),

    purchases AS (
        SELECT DISTINCT e.session_id
        FROM events e
        WHERE e.event_type = 'purchase'
            {variant_condition}
    )

    SELECT
        COUNT(DISTINCT sessions.session_id) AS total_sessions,
        COUNT(DISTINCT purchases.session_id) AS purchases,
        ROUND(
            COUNT(DISTINCT purchases.session_id)::numeric
            /
            NULLIF(COUNT(DISTINCT sessions.session_id), 0),
            4
        ) AS conversion_rate
    FROM sessions
    LEFT JOIN purchases
        ON sessions.session_id = purchases.session_id
    """

    return pd.read_sql(query, engine)


def get_filtered_funnel_metrics():
    variant_condition = get_variant_condition("e")

    query = f"""
    SELECT
        e.event_type,
        COUNT(*) AS total_events
    FROM events e
    WHERE 1 = 1
        {variant_condition}
    GROUP BY e.event_type
    ORDER BY total_events DESC
    """

    return pd.read_sql(query, engine)


def get_filtered_funnel_conversion():
    variant_condition = get_variant_condition("e")

    query = f"""
    WITH funnel AS (
        SELECT
            e.event_type,
            COUNT(DISTINCT e.session_id) AS sessions
        FROM events e
        WHERE e.event_type IN (
            'session_start',
            'view_product',
            'add_to_cart',
            'purchase'
        )
            {variant_condition}
        GROUP BY e.event_type
    )

    SELECT
        event_type,
        sessions
    FROM funnel
    ORDER BY
        CASE event_type
            WHEN 'session_start' THEN 1
            WHEN 'view_product' THEN 2
            WHEN 'add_to_cart' THEN 3
            WHEN 'purchase' THEN 4
        END
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        return df

    baseline = df["sessions"].iloc[0]

    df["conversion_from_start"] = (
        df["sessions"] / baseline
    ).round(4)

    df["dropoff_from_start"] = (
        1 - df["conversion_from_start"]
    ).round(4)

    return df


def get_filtered_conversion_by_channel():
    variant_condition = get_variant_condition("e")

    query = f"""
    WITH sessions AS (
        SELECT
            u.acquisition_channel,
            e.session_id
        FROM events e
        JOIN users u
            ON e.user_id = u.user_id
        WHERE e.event_type = 'session_start'
            {variant_condition}
    ),

    purchases AS (
        SELECT DISTINCT e.session_id
        FROM events e
        WHERE e.event_type = 'purchase'
            {variant_condition}
    )

    SELECT
        s.acquisition_channel,
        COUNT(DISTINCT s.session_id) AS total_sessions,
        COUNT(DISTINCT p.session_id) AS purchases,
        ROUND(
            COUNT(DISTINCT p.session_id)::numeric
            /
            NULLIF(COUNT(DISTINCT s.session_id), 0),
            4
        ) AS conversion_rate
    FROM sessions s
    LEFT JOIN purchases p
        ON s.session_id = p.session_id
    GROUP BY s.acquisition_channel
    ORDER BY conversion_rate DESC
    """

    return pd.read_sql(query, engine)


def get_filtered_conversion_by_device():
    variant_condition = get_variant_condition("e")

    query = f"""
    WITH sessions AS (
        SELECT
            u.device_type,
            e.session_id
        FROM events e
        JOIN users u
            ON e.user_id = u.user_id
        WHERE e.event_type = 'session_start'
            {variant_condition}
    ),

    purchases AS (
        SELECT DISTINCT e.session_id
        FROM events e
        WHERE e.event_type = 'purchase'
            {variant_condition}
    )

    SELECT
        s.device_type,
        COUNT(DISTINCT s.session_id) AS total_sessions,
        COUNT(DISTINCT p.session_id) AS purchases,
        ROUND(
            COUNT(DISTINCT p.session_id)::numeric
            /
            NULLIF(COUNT(DISTINCT s.session_id), 0),
            4
        ) AS conversion_rate
    FROM sessions s
    LEFT JOIN purchases p
        ON s.session_id = p.session_id
    GROUP BY s.device_type
    ORDER BY conversion_rate DESC
    """

    return pd.read_sql(query, engine)


def get_filtered_retention_data():
    variant_condition = get_variant_condition("e")

    query = f"""
    WITH cohort_size AS (

        SELECT
            DATE_TRUNC('week', signup_date)::date AS signup_week,
            COUNT(DISTINCT user_id) AS cohort_users
        FROM users
        GROUP BY DATE_TRUNC('week', signup_date)::date
    ),

    user_activity AS (

        SELECT
            u.user_id,
            DATE_TRUNC('week', u.signup_date)::date AS signup_week,
            e.event_date,
            FLOOR((e.event_date - u.signup_date) / 7) AS weeks_since_signup
        FROM users u
        JOIN events e
            ON u.user_id = e.user_id
        WHERE 1 = 1
            {variant_condition}
    ),

    retention_counts AS (

        SELECT
            signup_week,
            weeks_since_signup,
            COUNT(DISTINCT user_id) AS active_users
        FROM user_activity
        WHERE weeks_since_signup BETWEEN 0 AND 8
        GROUP BY signup_week, weeks_since_signup
    )

    SELECT
        r.signup_week,
        r.weeks_since_signup,
        ROUND(
            r.active_users::numeric
            /
            c.cohort_users,
            4
        ) AS retention_rate
    FROM retention_counts r
    JOIN cohort_size c
        ON r.signup_week = c.signup_week
    ORDER BY r.signup_week, r.weeks_since_signup
    """

    return pd.read_sql(query, engine)


# Load filtered dashboard data
dau_df = get_filtered_dau()
conversion_df = get_filtered_conversion_rate()
funnel_df = get_filtered_funnel_metrics()
channel_df = get_filtered_conversion_by_channel()
device_df = get_filtered_conversion_by_device()
funnel_conversion_df = get_filtered_funnel_conversion()
retention_df = get_filtered_retention_data()

# Global experiment comparison should always use both variants
experiment_df = get_experiment_results()
p_value = run_chi_square_test(experiment_df)

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

conversion_rate = conversion_df.iloc[0]["conversion_rate"]
total_events = funnel_df["total_events"].sum()

anomaly_df = detect_dau_anomalies()
historical_dau_df, forecast_df = forecast_dau()

forecast_insight = generate_forecast_insight(forecast_df)

experiment_insight = generate_experiment_insight(
    p_value,
    lift
)

channel_insight = generate_channel_insight(
    channel_df
)

device_insight = generate_device_insight(
    device_df
)

analytics_context = f"""
Selected variant: {selected_variant}

Selected variant conversion rate: {conversion_rate:.2%}

Control conversion rate: {control_rate:.2%}

Treatment conversion rate: {treatment_rate:.2%}

Experiment p-value: {p_value:.4f}

Treatment lift: {lift:.2f}%

Top acquisition channel:
{channel_df.iloc[0]['acquisition_channel']}

Top acquisition channel conversion rate:
{channel_df.iloc[0]['conversion_rate']:.2%}

Top device segment:
{device_df.iloc[0]['device_type']}

Top device conversion rate:
{device_df.iloc[0]['conversion_rate']:.2%}

Average 14-day forecasted DAU:
{forecast_df['forecasted_dau'].mean():.0f}
"""

# KPI cards
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    label="Conversion Rate",
    value=f"{conversion_rate * 100:.2f}%"
)

col2.metric(
    label="Total Events",
    value=f"{total_events:,}"
)

col3.metric(
    label="P-Value",
    value=round(p_value, 4)
)

col4.metric(
    label="Treatment Lift",
    value=f"{lift:.2f}%"
)

st.caption(
    "Note: Variant filter applies to product metrics, funnel, segmentation, and retention. "
    "A/B test p-value and treatment lift intentionally compare control vs treatment globally."
)

st.header("Executive Insights")

st.info(experiment_insight)
st.success(channel_insight)
st.warning(device_insight)

st.header("AI Analytics Assistant")

user_query = st.text_input(
    "Ask a product analytics question",
    placeholder="Example: What is the conversion rate?"
)

if user_query:
    response = answer_query(user_query)

    if hasattr(response, "to_dict"):
        st.dataframe(
            response,
            use_container_width=True
        )
    else:
        st.info(response)

st.header("LLM Product Analytics Assistant")

llm_query = st.text_area(
    "Ask strategic analytics questions",
    placeholder="Example: Why is the experiment underperforming?"
)

if st.button("Generate AI Insight"):

    if not llm_query.strip():
        st.warning("Enter a question before generating an insight.")
    else:
        with st.spinner("Generating insight..."):

            llm_response = generate_llm_response(
                llm_query,
                analytics_context
            )

            st.success(llm_response)

# DAU chart
dau_chart = px.line(
    dau_df,
    x="event_date",
    y="dau",
    title=f"Daily Active Users - {selected_variant}"
)

st.plotly_chart(
    dau_chart,
    use_container_width=True
)

st.subheader("DAU Anomaly Detection")

st.caption(
    "Anomaly detection currently runs on global DAU to monitor overall platform health."
)

anomaly_chart = px.scatter(
    anomaly_df,
    x="event_date",
    y="dau",
    color="is_anomaly",
    title="Detected Anomalies in Daily Active Users"
)

st.plotly_chart(
    anomaly_chart,
    use_container_width=True
)

st.dataframe(
    anomaly_df[anomaly_df["is_anomaly"]],
    use_container_width=True
)

st.subheader("DAU Forecast")

st.caption(
    "Forecast currently uses global DAU as an operational baseline."
)

forecast_chart = px.line(
    historical_dau_df,
    x="event_date",
    y="dau",
    title="Historical DAU with 14-Day Forecast"
)

forecast_chart.add_scatter(
    x=forecast_df["event_date"],
    y=forecast_df["forecasted_dau"],
    mode="lines",
    name="Forecasted DAU"
)

st.plotly_chart(
    forecast_chart,
    use_container_width=True
)

st.dataframe(
    forecast_df,
    use_container_width=True
)

st.info(forecast_insight)

# Funnel chart
funnel_chart = px.bar(
    funnel_df,
    x="event_type",
    y="total_events",
    title=f"Funnel Event Distribution - {selected_variant}"
)

st.plotly_chart(
    funnel_chart,
    use_container_width=True
)

st.subheader("Funnel Conversion from Session Start")

funnel_conversion_chart = px.bar(
    funnel_conversion_df,
    x="event_type",
    y="conversion_from_start",
    title=f"Funnel Conversion Rate by Step - {selected_variant}",
    text="conversion_from_start"
)

funnel_conversion_chart.update_traces(
    texttemplate="%{text:.1%}",
    textposition="outside"
)

funnel_conversion_chart.update_layout(
    yaxis_tickformat=".0%"
)

st.plotly_chart(
    funnel_conversion_chart,
    use_container_width=True
)

st.dataframe(
    funnel_conversion_df,
    use_container_width=True
)

# Experiment section
st.header("A/B Experiment Results")

st.dataframe(
    experiment_df,
    use_container_width=True
)

if p_value < 0.05:
    st.success(
        "Treatment variant shows statistically significant impact."
    )
else:
    st.warning(
        "No statistically significant difference detected between variants."
    )

st.header("Segment Performance")

seg_col1, seg_col2 = st.columns(2)

channel_chart = px.bar(
    channel_df,
    x="acquisition_channel",
    y="conversion_rate",
    title=f"Conversion Rate by Acquisition Channel - {selected_variant}"
)

device_chart = px.bar(
    device_df,
    x="device_type",
    y="conversion_rate",
    title=f"Conversion Rate by Device Type - {selected_variant}"
)

seg_col1.plotly_chart(
    channel_chart,
    use_container_width=True
)

seg_col2.plotly_chart(
    device_chart,
    use_container_width=True
)

# Retention section
st.header("Retention Analysis")

retention_pivot = retention_df.pivot(
    index="signup_week",
    columns="weeks_since_signup",
    values="retention_rate"
)

retention_heatmap = px.imshow(
    retention_pivot,
    aspect="auto",
    color_continuous_scale="Blues",
    labels=dict(
        x="Weeks Since Signup",
        y="Signup Cohort Week",
        color="Retention Rate"
    ),
    title=f"Weekly Cohort Retention - {selected_variant}"
)

retention_heatmap.update_layout(
    height=500
)

st.plotly_chart(
    retention_heatmap,
    use_container_width=True
)