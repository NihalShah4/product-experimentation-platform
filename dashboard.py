import streamlit as st
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
    get_conversion_by_device
)

from src.insights import (
    generate_experiment_insight,
    generate_channel_insight,
    generate_device_insight
)

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

# Load data
dau_df = get_daily_active_users()
conversion_df = get_conversion_rate()
funnel_df = get_funnel_metrics()
experiment_df = get_experiment_results()
retention_df = get_retention_data()
channel_df = get_conversion_by_channel()
device_df = get_conversion_by_device()

# Calculate metrics
conversion_rate = conversion_df.iloc[0]["conversion_rate"]
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

# KPI cards
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    label="Conversion Rate",
    value=f"{conversion_rate * 100:.2f}%"
)

col2.metric(
    label="Total Events",
    value=f"{funnel_df['total_events'].sum():,}"
)

col3.metric(
    label="P-Value",
    value=round(p_value, 4)
)

col4.metric(
    label="Treatment Lift",
    value=f"{lift:.2f}%"
)

st.header("Executive Insights")

st.info(experiment_insight)

st.success(channel_insight)

st.warning(device_insight)

# DAU chart
dau_chart = px.line(
    dau_df,
    x="event_date",
    y="dau",
    title="Daily Active Users"
)

st.plotly_chart(
    dau_chart,
    use_container_width=True
)

# Funnel chart
funnel_chart = px.bar(
    funnel_df,
    x="event_type",
    y="total_events",
    title="Funnel Event Distribution"
)

st.plotly_chart(
    funnel_chart,
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
    title="Conversion Rate by Acquisition Channel"
)

device_chart = px.bar(
    device_df,
    x="device_type",
    y="conversion_rate",
    title="Conversion Rate by Device Type"
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
    index="signup_date",
    columns="days_since_signup",
    values="retention_rate"
)

retention_heatmap = px.imshow(
    retention_pivot,
    aspect="auto",
    color_continuous_scale="Blues",
    labels=dict(
        x="Days Since Signup",
        y="Signup Cohort",
        color="Retention"
    ),
    title="30-Day Cohort Retention"
)

retention_heatmap.update_layout(
    height=600
)

st.plotly_chart(
    retention_heatmap,
    use_container_width=True
)