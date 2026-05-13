"""
dashboard.py

Product Intelligence Platform

Purpose:
This is the main Streamlit application for the Product Intelligence Platform.
It combines product analytics, experimentation, forecasting, anomaly detection,
guarded simulation, and LLM-assisted executive insights into one interactive
dashboard.

Core Modules:
- Executive KPI monitoring
- Product funnel analytics
- A/B experiment evaluation
- Acquisition and device segmentation
- Weekly cohort retention
- DAU forecasting
- DAU anomaly detection
- Guarded synthetic data simulation
- Rule-based and LLM-powered analytics assistants

Architecture:
- Streamlit handles the user interface
- PostgreSQL stores synthetic product-event data
- pandas executes SQL result processing
- Plotly renders interactive visualizations
- scikit-learn supports anomaly detection
- OpenAI powers strategic interpretation through the LLM assistant

Design Intent:
This app is built to simulate an internal executive-facing product analytics
system, not a simple notebook dashboard.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from src.simulation_engine import generate_simulation_data

from src.experiment_analysis import (
    get_experiment_results,
    run_chi_square_test
)

from src.metrics import (
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
    page_title="Product Intelligence Platform",
    layout="wide"
)

# =========================================================
# GLOBAL PAGE STYLING
# =========================================================
# Custom CSS is used to move beyond default Streamlit styling.
# The goal is to create an executive-grade analytics interface
# with premium visual hierarchy, dark theme, KPI cards, tabs,
# chart containers, and product-style interaction patterns.

st.markdown(
    """
    <style>

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(30, 64, 175, 0.22), transparent 32%),
                radial-gradient(circle at top right, rgba(14, 165, 233, 0.12), transparent 25%),
                linear-gradient(135deg, #020617 0%, #081226 45%, #020617 100%);
            color: #f8fafc;
        }

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(2,6,23,1) 0%, rgba(15,23,42,1) 100%);
            border-right: 1px solid rgba(148, 163, 184, 0.12);
        }

        .block-container {
            padding-top: 4.5rem;
            padding-bottom: 4rem;
            max-width: 1500px;
        }

        .main-title {
            font-size: 52px;
            font-weight: 900;
            letter-spacing: -2px;
            color: #f8fafc;
            line-height: 1.15;
            margin-top: 20px;
            margin-bottom: 14px;
        }
        .subtitle {
            font-size: 19px;
            color: #94a3b8;
            margin-bottom: 42px;
            max-width: 1100px;
            line-height: 1.6;
        }

        .section-title {
            font-size: 34px;
            font-weight: 800;
            color: #f8fafc;
            margin-top: 44px;
            margin-bottom: 8px;
            letter-spacing: -1px;
        }

        .section-subtitle {
            font-size: 15px;
            color: #94a3b8;
            margin-bottom: 24px;
        }

        .kpi-card {
            position: relative;
            overflow: hidden;

            background:
                linear-gradient(
                    145deg,
                    rgba(15,23,42,0.92),
                    rgba(2,6,23,0.92)
                );

            border: 1px solid rgba(148,163,184,0.12);

            border-radius: 22px;

            padding: 28px;

            backdrop-filter: blur(12px);

            box-shadow:
                0 10px 40px rgba(0,0,0,0.35),
                inset 0 1px 0 rgba(255,255,255,0.04);

            transition:
                transform 0.25s ease,
                box-shadow 0.25s ease,
                border 0.25s ease;
        }

        .kpi-card:hover {
            transform: translateY(-6px);

            border: 1px solid rgba(96,165,250,0.35);

            box-shadow:
                0 18px 50px rgba(37,99,235,0.18),
                0 10px 30px rgba(0,0,0,0.45);
        }

        .kpi-card::before {
            content: "";

            position: absolute;

            width: 220px;
            height: 220px;

            background:
                radial-gradient(
                    circle,
                    rgba(59,130,246,0.18),
                    transparent 70%
                );

            top: -120px;
            right: -100px;
        }

        .kpi-label {
            font-size: 13px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 14px;
            font-weight: 600;
        }

        .kpi-value {
            font-size: 44px;
            font-weight: 900;
            color: #f8fafc;
            letter-spacing: -2px;
            line-height: 1;
        }

        .kpi-note {
            margin-top: 16px;
            font-size: 14px;
            color: #38bdf8;
            font-weight: 500;
        }

        .note-box {
            background:
                linear-gradient(
                    135deg,
                    rgba(15,23,42,0.95),
                    rgba(2,6,23,0.85)
                );

            border: 1px solid rgba(148,163,184,0.12);

            border-radius: 18px;

            padding: 18px 22px;

            color: #cbd5e1;

            margin-top: 18px;
            margin-bottom: 30px;

            backdrop-filter: blur(10px);
        }

        .insight-card-blue {
            background:
                linear-gradient(
                    135deg,
                    rgba(37,99,235,0.20),
                    rgba(14,165,233,0.08)
                );

            border: 1px solid rgba(56,189,248,0.22);

            border-radius: 20px;

            padding: 22px;

            color: #dbeafe;

            margin-bottom: 18px;

            box-shadow:
                0 8px 30px rgba(14,165,233,0.08);
        }

        .insight-card-green {
            background:
                linear-gradient(
                    135deg,
                    rgba(34,197,94,0.18),
                    rgba(16,185,129,0.08)
                );

            border: 1px solid rgba(74,222,128,0.22);

            border-radius: 20px;

            padding: 22px;

            color: #dcfce7;

            margin-bottom: 18px;

            box-shadow:
                0 8px 30px rgba(34,197,94,0.08);
        }

        .insight-card-amber {
            background:
                linear-gradient(
                    135deg,
                    rgba(245,158,11,0.18),
                    rgba(234,179,8,0.06)
                );

            border: 1px solid rgba(251,191,36,0.22);

            border-radius: 20px;

            padding: 22px;

            color: #fef3c7;

            margin-bottom: 18px;

            box-shadow:
                0 8px 30px rgba(245,158,11,0.08);
        }

        div[data-testid="stMetric"] {
            background: rgba(15,23,42,0.88);
            border-radius: 18px;
            padding: 18px;
            border: 1px solid rgba(148,163,184,0.12);
        }

        div[data-testid="stDataFrame"] {
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid rgba(148,163,184,0.08);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 28px;

            background:
                rgba(2, 6, 23, 0.72);

            padding:
                14px 18px;

            border-radius: 18px;

            border:
                1px solid rgba(148,163,184,0.10);

            backdrop-filter:
                blur(14px);

            margin-bottom: 34px;

            box-shadow:
                0 10px 30px rgba(0,0,0,0.22);
        }

        .stTabs [data-baseweb="tab"] {
            color: #94a3b8;

            font-size: 15px;

            font-weight: 700;

            letter-spacing: 0.2px;

            padding:
                10px 6px;

            transition:
                all 0.25s ease;

            border-radius: 10px;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #f8fafc;

            transform:
                translateY(-1px);
        }

        .stTabs [aria-selected="true"] {
            color: #38bdf8 !important;

            background:
                rgba(14,165,233,0.08);

            box-shadow:
                inset 0 -2px 0 #38bdf8,
                0 0 14px rgba(56,189,248,0.18);

            border-radius: 10px;
        }
        .stButton>button {
            background:
                linear-gradient(
                    135deg,
                    #2563eb,
                    #1d4ed8
                );

            color: white;

            border: none;

            border-radius: 14px;

            padding: 0.7rem 1.3rem;

            font-weight: 700;

            transition: all 0.25s ease;
        }

        .stButton>button:hover {
            transform: translateY(-2px);

            box-shadow:
                0 10px 25px rgba(37,99,235,0.35);
        }
        
        .trend-positive {
            margin-top: 14px;
            color: #4ade80;
            font-size: 14px;
            font-weight: 700;
        }

        .trend-negative {
            margin-top: 14px;
            color: #f87171;
            font-size: 14px;
            font-weight: 700;
        }

        .trend-neutral {
            margin-top: 14px;
            color: #facc15;
            font-size: 14px;
            font-weight: 700;
        }
        
        div[data-testid="stPlotlyChart"] {
            background:
                linear-gradient(
                    145deg,
                    rgba(15,23,42,0.88),
                    rgba(2,6,23,0.88)
                );

            border:
                1px solid rgba(148,163,184,0.12);

            border-radius:
                22px;

            padding:
                18px;

            box-shadow:
                0 10px 35px rgba(0,0,0,0.25);

            margin-bottom:
                28px;
        }

        .copilot-card {
            background:
                linear-gradient(
                    145deg,
                    rgba(15,23,42,0.92),
                    rgba(2,6,23,0.92)
                );

            border: 1px solid rgba(56,189,248,0.18);
            border-radius: 24px;
            padding: 28px;
            box-shadow:
                0 16px 45px rgba(14,165,233,0.08),
                inset 0 1px 0 rgba(255,255,255,0.04);
            margin-bottom: 24px;
        }

        .copilot-badge {
            display: inline-block;
            background: rgba(14,165,233,0.12);
            color: #38bdf8;
            border: 1px solid rgba(56,189,248,0.25);
            border-radius: 999px;
            padding: 6px 12px;
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 16px;
        }

        .prompt-chip {
            display: inline-block;
            background: rgba(15,23,42,0.95);
            color: #cbd5e1;
            border: 1px solid rgba(148,163,184,0.18);
            border-radius: 999px;
            padding: 8px 12px;
            margin: 4px 6px 8px 0;
            font-size: 13px;
        }

        .decision-card {
            background:
                linear-gradient(
                    145deg,
                    rgba(15,23,42,0.92),
                    rgba(2,6,23,0.92)
                );
            border: 1px solid rgba(248,113,113,0.22);
            border-radius: 22px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 14px 40px rgba(248,113,113,0.06);
        }

        .decision-label {
            color: #94a3b8;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .decision-value {
            color: #f87171;
            font-size: 32px;
            font-weight: 900;
            margin-bottom: 10px;
        }

        .decision-text {
            color: #cbd5e1;
            font-size: 15px;
            line-height: 1.6;
        }

        .strategy-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 18px;
            margin-top: 18px;
            margin-bottom: 34px;
        }

        .strategy-card {
            background:
                linear-gradient(
                    145deg,
                    rgba(15,23,42,0.92),
                    rgba(2,6,23,0.92)
                );
            border: 1px solid rgba(148,163,184,0.14);
            border-radius: 20px;
            padding: 22px;
            box-shadow: 0 12px 34px rgba(0,0,0,0.24);
        }

        .strategy-label {
            color: #94a3b8;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 12px;
        }

        .strategy-title {
            color: #f8fafc;
            font-size: 20px;
            font-weight: 900;
            margin-bottom: 10px;
        }

        .strategy-text {
            color: #cbd5e1;
            font-size: 14px;
            line-height: 1.55;
        }

        .footer-panel {
            margin-top: 60px;
            margin-bottom: 30px;
            padding: 28px;
            border-radius: 24px;
            background:
                linear-gradient(
                    145deg,
                    rgba(15,23,42,0.92),
                    rgba(2,6,23,0.92)
                );
            border: 1px solid rgba(59,130,246,0.18);
        }

        .footer-title {
            color: #f8fafc;
            font-size: 26px;
            font-weight: 900;
            margin-bottom: 24px;
        }

        .footer-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 18px;
        }

        .footer-card {
            padding: 18px;
            border-radius: 18px;
            background: rgba(15,23,42,0.65);
            border: 1px solid rgba(148,163,184,0.12);
        }

        .footer-label {
            color: #38bdf8;
            font-size: 12px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }

        .footer-text {
            color: #cbd5e1;
            line-height: 1.6;
            font-size: 14px;
        }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR CONTROLS
# =========================================================
# Sidebar controls define global dashboard filters and expose
# platform modules. The experiment variant selector controls
# filtered product metrics while global A/B comparison metrics
# intentionally remain unfiltered.

st.sidebar.markdown("## Analytics Controls")

selected_variant = st.sidebar.selectbox(
    "Experiment Variant",
    ["All", "control", "treatment"]
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Platform Modules**
    - Executive Insights
    - AI Analytics Assistant
    - Experimentation
    - Funnel Analytics
    - Forecasting
    - Anomaly Detection
    - Retention Cohorts
    """
)

# =========================================================
# SESSION STATE GUARDRAILS
# =========================================================
# Streamlit session state is used to prevent repeated database
# regeneration during a single app session. This protects the
# simulation workflow from uncontrolled repeated writes.

if "simulation_generated" not in st.session_state:
    st.session_state["simulation_generated"] = False
    
if "simulation_result" not in st.session_state:
    st.session_state["simulation_result"] = None

# =========================================================
# VARIANT FILTER CONSTRUCTION
# =========================================================
# Builds a reusable SQL condition for the selected experiment
# variant.
#
# If "All" is selected, no filter is applied.
# If "control" or "treatment" is selected, the condition is
# injected into filtered product analytics queries.
#
# This keeps dashboard interactivity centralized and avoids
# duplicating variant-filter logic inside every SQL query.

def get_variant_condition(alias="e"):
    if selected_variant == "All":
        return ""
    return f"AND {alias}.variant = '{selected_variant}'"

# =========================================================
# FILTERED DAILY ACTIVE USERS
# =========================================================
# Computes Daily Active Users after applying the selected
# experiment variant filter.
#
# Used by:
# - Command Center DAU trend
# - product health monitoring
# - variant-level engagement comparison

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

# =========================================================
# FILTERED CONVERSION RATE
# =========================================================
# Computes conversion rate for the selected dashboard scope.
#
# Conversion definition:
# purchase sessions / session_start sessions
#
# NULLIF prevents division-by-zero errors when a filtered
# segment has no sessions.

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

# =========================================================
# FILTERED FUNNEL EVENT DISTRIBUTION
# =========================================================
# Counts product events across the funnel after applying the
# selected variant filter.
#
# This supports visibility into how users move through:
# session_start -> view_product -> add_to_cart -> purchase

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

# =========================================================
# FILTERED FUNNEL CONVERSION ANALYSIS
# =========================================================
# Computes conversion and drop-off from the funnel entry point.
#
# session_start is used as the baseline denominator.
#
# Output columns:
# - event_type
# - sessions
# - conversion_from_start
# - dropoff_from_start

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

# =========================================================
# FILTERED ACQUISITION CHANNEL ANALYSIS
# =========================================================
# Computes conversion performance by acquisition channel.
#
# Used to identify which marketing/source channels generate
# the highest-quality traffic under the selected variant scope.

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

# =========================================================
# FILTERED DEVICE SEGMENT ANALYSIS
# =========================================================
# Computes conversion performance by device type.
#
# Used to evaluate whether desktop, mobile, or tablet users
# convert more effectively under the selected variant scope.

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

# =========================================================
# FILTERED WEEKLY COHORT RETENTION
# =========================================================
# Computes weekly retention by signup cohort.
#
# Retention logic:
# - users are grouped by signup week
# - later activity is mapped to weeks since signup
# - active users are divided by original cohort size
#
# This supports product stickiness and engagement analysis.

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

# =========================================================
# DATA LOADING + METRIC COMPUTATION
# =========================================================
# The following calls execute the dashboard's core analytical
# queries.
#
# Filtered metrics respect the sidebar variant selector:
# - DAU
# - conversion rate
# - funnel metrics
# - channel segmentation
# - device segmentation
# - retention
#
# Global experiment metrics intentionally ignore the sidebar
# filter because p-value and treatment lift require both
# control and treatment groups.

dau_df = get_filtered_dau()
conversion_df = get_filtered_conversion_rate()
funnel_df = get_filtered_funnel_metrics()
channel_df = get_filtered_conversion_by_channel()
device_df = get_filtered_conversion_by_device()
funnel_conversion_df = get_filtered_funnel_conversion()
retention_df = get_filtered_retention_data()

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

# =========================================================
# HERO SECTION
# =========================================================
# Introduces the platform as an executive-facing product
# intelligence system rather than a simple analytics dashboard.

st.markdown(
    """
    <div class="main-title">Product Intelligence Platform</div>
    <div class="subtitle">
        Executive-grade experimentation, funnel analytics, retention intelligence, anomaly monitoring, and LLM-assisted product decision support.
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# DYNAMIC KPI TREND LABELS
# =========================================================

conversion_trend_class = (
    "trend-positive"
    if conversion_rate >= control_rate
    else "trend-negative"
)

conversion_trend_text = (
    f"▲ {(conversion_rate - control_rate) * 100:.2f} pts vs control"
    if conversion_rate >= control_rate
    else f"▼ {(conversion_rate - control_rate) * 100:.2f} pts vs control"
)

events_trend_text = f"● {total_events:,} filtered events"
events_trend_class = "trend-neutral"

p_value_trend_class = (
    "trend-positive"
    if p_value < 0.05
    else "trend-neutral"
)

p_value_trend_text = (
    "● Statistically significant"
    if p_value < 0.05
    else "● Not statistically significant"
)

lift_trend_class = (
    "trend-positive"
    if lift > 0
    else "trend-negative"
)

lift_trend_text = (
    f"▲ {lift:.2f}% treatment improvement"
    if lift > 0
    else f"▼ {lift:.2f}% treatment decline"
)

# =========================================================
# EXECUTIVE KPI CARDS
# =========================================================
# Displays the highest-priority product and experiment metrics
# in a leadership-readable format.
#
# These cards are designed to communicate:
# - current product conversion
# - event volume
# - experiment confidence
# - treatment performance

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f'''
<div class="kpi-card">
    <div class="kpi-label">Conversion Rate</div>
    <div class="kpi-value">{conversion_rate:.2%}</div>
    <div class="{conversion_trend_class}">{conversion_trend_text}</div>
    <div class="kpi-note">Selected Variant: {selected_variant}</div>
</div>
''',
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f'''
<div class="kpi-card">
    <div class="kpi-label">Total Events</div>
    <div class="kpi-value">{total_events:,}</div>
    <div class="{events_trend_class}">{events_trend_text}</div>
    <div class="kpi-note">Filtered product activity</div>
</div>
''',
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f'''
<div class="kpi-card">
    <div class="kpi-label">Experiment P-Value</div>
    <div class="kpi-value">{p_value:.4f}</div>
    <div class="{p_value_trend_class}">{p_value_trend_text}</div>
    <div class="kpi-note">Global A/B comparison</div>
</div>
''',
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f'''
<div class="kpi-card">
    <div class="kpi-label">Treatment Lift</div>
    <div class="kpi-value">{lift:.2f}%</div>
    <div class="{lift_trend_class}">{lift_trend_text}</div>
    <div class="kpi-note">Treatment vs control</div>
</div>
''',
        unsafe_allow_html=True
    )

st.markdown(
    """
    <div class="note-box">
        Variant filter applies to product metrics, funnel, segmentation, and retention. 
        A/B test p-value and treatment lift intentionally compare control vs treatment globally.
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# EXECUTIVE DECISION SUMMARY
# =========================================================
# Converts analytical outputs into concise business-facing
# interpretations for stakeholders.

st.markdown('<div class="section-title">Executive Decision Summary</div>', unsafe_allow_html=True)
st.markdown('<div class="section-subtitle">Automated interpretation of experimentation, segment performance, and product behavior.</div>', unsafe_allow_html=True)

st.markdown(f'<div class="insight-card-blue">{experiment_insight}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="insight-card-green">{channel_insight}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="insight-card-amber">{device_insight}</div>', unsafe_allow_html=True)

# =========================================================
# STRATEGIC RECOMMENDATIONS
# =========================================================
# Provides leadership-facing next-best actions based on
# experiment results, segment performance, and forecast risk.

st.markdown(
    '<div class="section-title">Strategic Recommendations</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">Leadership-facing interpretation of risk, opportunity, and next-best actions.</div>',
    unsafe_allow_html=True
)

strategy_html = f"""
<div class="strategy-grid">
<div class="strategy-card">
<div class="strategy-label">Experiment Risk</div>
<div class="strategy-title">Pause rollout</div>
<div class="strategy-text">
Treatment lift is {lift:.2f}% with p-value {p_value:.4f}. Current evidence does not support shipping the treatment broadly.
</div>
</div>

<div class="strategy-card">
<div class="strategy-label">Growth Opportunity</div>
<div class="strategy-title">Double down on email</div>
<div class="strategy-text">
Email is the strongest acquisition channel at {channel_df.iloc[0]['conversion_rate']:.2%}. Prioritize email-led lifecycle experiments.
</div>
</div>

<div class="strategy-card">
<div class="strategy-label">Segment Focus</div>
<div class="strategy-title">Optimize desktop flow</div>
<div class="strategy-text">
{device_df.iloc[0]['device_type'].capitalize()} users show the strongest conversion at {device_df.iloc[0]['conversion_rate']:.2%}. Use this segment as the initial optimization benchmark.
</div>
</div>

<div class="strategy-card">
<div class="strategy-label">Forecast Watch</div>
<div class="strategy-title">Monitor DAU contraction</div>
<div class="strategy-text">
Forecasted DAU is approximately {forecast_df['forecasted_dau'].mean():.0f} users/day. Track retention and acquisition quality before expanding rollout.
</div>
</div>
</div>
"""

st.markdown(strategy_html, unsafe_allow_html=True)

# =========================================================
# PRIMARY DASHBOARD NAVIGATION
# =========================================================
# Tabs organize the platform into executive product modules:
# simulation, health monitoring, experimentation, growth,
# retention, and AI-assisted analytics.

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "Simulation Lab",
        "Command Center",
        "Experimentation",
        "Growth Segments",
        "Retention",
        "AI Copilot"        
    ]
)

# =========================================================
# SIMULATION LAB TAB
# =========================================================
# Provides controlled synthetic data generation for demo and
# testing workflows.
#
# Guardrails:
# - capped user generation
# - capped date range
# - randomized actual user count
# - one generation per Streamlit session
# - synthetic data only
#
# This demonstrates safe database write operations and
# simulation-driven analytics testing.

with tab1:
    st.markdown(
        '<div class="section-title">Simulation Lab</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">Generate guarded synthetic product-event data and update PostgreSQL dynamically.</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div class="copilot-card">
    <div class="copilot-badge">SAFE DATA GENERATION</div>
    <div class="section-subtitle">
        This module allows controlled synthetic data generation with strict guardrails:
        capped user volume, capped date range, randomized actual records, and one generation per session.
    </div>
</div>
""",
        unsafe_allow_html=True
    )

    sim_col1, sim_col2 = st.columns(2)

    with sim_col1:
        selected_user_cap = st.selectbox(
            "Maximum users",
            [1000, 5000, 10000]
        )

    with sim_col2:
        selected_date_range = st.selectbox(
            "Date range",
            [30, 60, 90]
        )

    st.markdown(
        f"""
<div class="note-box">
    Selected guardrails: system will generate between 
    {int(selected_user_cap * 0.90):,} and {selected_user_cap:,} users 
    across {selected_date_range} days.
</div>
""",
        unsafe_allow_html=True
    )

# Generation is disabled after one successful run to prevent
# repeated database resets within the same session.

    generate_button = st.button(
        "Generate New Simulation",
        disabled=st.session_state["simulation_generated"]
    )

    if generate_button:

        with st.spinner(
            "Generating synthetic product-event data and updating PostgreSQL..."
        ):
            
            # Generates synthetic users/events and writes them into
            # PostgreSQL after clearing the existing synthetic dataset.
            result = generate_simulation_data(
                max_users=selected_user_cap,
                date_range_days=selected_date_range
            )

            # Persist simulation results in session state so they remain
            # visible after Streamlit reruns the app.
            st.session_state["simulation_result"] = result
            st.session_state["simulation_generated"] = True
            # Force immediate rerun so the button lock is applied visually.
            st.rerun()

            st.success(
                "Simulation generated successfully. Refresh the app session to generate again."
            )

            st.markdown(
                f"""
                <div class="strategy-grid">
                <div class="strategy-card">
                <div class="strategy-label">Requested Cap</div>
                <div class="strategy-title">{result['requested_max_users']:,}</div>
                <div class="strategy-text">Maximum users selected by the user.</div>
                </div>

                <div class="strategy-card">
                <div class="strategy-label">Actual Users</div>
                <div class="strategy-title">{result['actual_users']:,}</div>
                <div class="strategy-text">Randomized within the safe 90–100% generation band.</div>
                </div>

                <div class="strategy-card">
                <div class="strategy-label">Events Generated</div>
                <div class="strategy-title">{result['events_generated']:,}</div>
                <div class="strategy-text">Synthetic product-event records inserted into PostgreSQL.</div>
                </div>

                <div class="strategy-card">
                <div class="strategy-label">Date Range</div>
                <div class="strategy-title">{result['date_range_days']} days</div>
                <div class="strategy-text">Controlled simulation period used for event generation.</div>
                </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.warning(
                "Data has been regenerated. Refresh the page to reload all dashboard metrics from the updated database."
            )
    
    # Displays the persisted simulation summary after rerun.
    if st.session_state["simulation_result"] is not None:
        result = st.session_state["simulation_result"]

        st.success(
            "Simulation generated successfully. Refresh the app session to generate again."
        )

        st.markdown(
            f"""
            <div class="strategy-grid">
            <div class="strategy-card">
            <div class="strategy-label">Requested Cap</div>
            <div class="strategy-title">{result['requested_max_users']:,}</div>
            <div class="strategy-text">Maximum users selected by the user.</div>
            </div>

            <div class="strategy-card">
            <div class="strategy-label">Actual Users</div>
            <div class="strategy-title">{result['actual_users']:,}</div>
            <div class="strategy-text">Randomized within the safe 90–100% generation band.</div>
            </div>

            <div class="strategy-card">
            <div class="strategy-label">Events Generated</div>
            <div class="strategy-title">{result['events_generated']:,}</div>
            <div class="strategy-text">Synthetic product-event records inserted into PostgreSQL.</div>
            </div>

            <div class="strategy-card">
            <div class="strategy-label">Date Range</div>
            <div class="strategy-title">{result['date_range_days']} days</div>
            <div class="strategy-text">Controlled simulation period used for event generation.</div>
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.warning(
        "Data has been regenerated. Dashboard metrics are now reloaded from the updated database."
    )

    if st.session_state["simulation_generated"]:
        st.info(
            "Simulation generation is locked for this session to prevent repeated database resets."
        )

# =========================================================
# COMMAND CENTER TAB
# =========================================================
# Monitors product health through DAU trends, anomaly detection,
# and short-term forecasting.

with tab2:
    st.markdown('<div class="section-title">Product Health Command Center</div>', unsafe_allow_html=True)

    dau_chart = px.line(
        dau_df,
        x="event_date",
        y="dau",
        title=f"Daily Active Users - {selected_variant}",
        template="plotly_dark"
    )

    dau_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e5e7eb"
    )

    st.plotly_chart(
        dau_chart,
        use_container_width=True
    )

    st.markdown('<div class="section-title">DAU Anomaly Detection</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Isolation Forest monitoring for abnormal product activity movement.</div>', unsafe_allow_html=True)

    anomaly_chart = px.scatter(
        anomaly_df,
        x="event_date",
        y="dau",
        color="is_anomaly",
        title="Detected Anomalies in Daily Active Users",
        template="plotly_dark"
    )

    anomaly_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e5e7eb"
    )

    st.plotly_chart(
        anomaly_chart,
        use_container_width=True
    )

    with st.expander("View detected anomalies"):
        st.dataframe(
            anomaly_df[anomaly_df["is_anomaly"]],
            use_container_width=True
        )

    st.markdown('<div class="section-title">DAU Forecast</div>', unsafe_allow_html=True)

    forecast_chart = px.line(
        historical_dau_df,
        x="event_date",
        y="dau",
        title="Historical DAU with 14-Day Forecast",
        template="plotly_dark"
    )

    forecast_chart.add_scatter(
        x=forecast_df["event_date"],
        y=forecast_df["forecasted_dau"],
        mode="lines",
        name="Forecasted DAU"
    )

    forecast_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e5e7eb"
    )

    st.plotly_chart(
        forecast_chart,
        use_container_width=True
    )

    st.markdown(f'<div class="insight-card-blue">{forecast_insight}</div>', unsafe_allow_html=True)

# =========================================================
# EXPERIMENTATION TAB
# =========================================================
# Supports A/B test interpretation, rollout decisions, funnel
# performance, and conversion drop-off analysis.

with tab3:
    st.markdown('<div class="section-title">Experimentation Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Control vs treatment conversion comparison with statistical decision support.</div>', unsafe_allow_html=True)

    rollout_decision = (
        "Recommend rollout"
        if p_value < 0.05 and lift > 0
        else "Do not recommend rollout"
    )

    decision_reason = (
        "Treatment shows statistically significant positive lift."
        if p_value < 0.05 and lift > 0
        else "Treatment does not show statistically significant positive impact."
    )

    st.markdown(
        f'''
    <div class="decision-card">
        <div class="decision-label">Experiment Decision</div>
        <div class="decision-value">{rollout_decision}</div>
        <div class="decision-text">
            {decision_reason} Current treatment lift is {lift:.2f}% with a p-value of {p_value:.4f}.
        </div>
    </div>
    ''',
        unsafe_allow_html=True
    )

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

    st.markdown('<div class="section-title">Funnel Event Distribution</div>', unsafe_allow_html=True)

    funnel_chart = px.bar(
        funnel_df,
        x="event_type",
        y="total_events",
        title=f"Funnel Event Distribution - {selected_variant}",
        template="plotly_dark"
    )

    funnel_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e5e7eb"
    )

    st.plotly_chart(
        funnel_chart,
        use_container_width=True
    )

    st.markdown('<div class="section-title">Funnel Conversion from Session Start</div>', unsafe_allow_html=True)

    funnel_conversion_chart = px.bar(
        funnel_conversion_df,
        x="event_type",
        y="conversion_from_start",
        title=f"Funnel Conversion Rate by Step - {selected_variant}",
        text="conversion_from_start",
        template="plotly_dark"
    )

    funnel_conversion_chart.update_traces(
        texttemplate="%{text:.1%}",
        textposition="outside"
    )

    funnel_conversion_chart.update_layout(
        yaxis_tickformat=".0%",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e5e7eb"
    )

    st.plotly_chart(
        funnel_conversion_chart,
        use_container_width=True
    )

    with st.expander("View funnel conversion table"):
        st.dataframe(
            funnel_conversion_df,
            use_container_width=True
        )

# =========================================================
# GROWTH SEGMENTS TAB
# =========================================================
# Compares conversion performance across acquisition channels
# and device segments.

with tab4:
    st.markdown('<div class="section-title">Growth Segment Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Conversion performance across acquisition channels and device segments.</div>', unsafe_allow_html=True)

    seg_col1, seg_col2 = st.columns(2)

    channel_chart = px.bar(
        channel_df,
        x="acquisition_channel",
        y="conversion_rate",
        title=f"Conversion Rate by Acquisition Channel - {selected_variant}",
        template="plotly_dark"
    )

    channel_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e5e7eb"
    )

    device_chart = px.bar(
        device_df,
        x="device_type",
        y="conversion_rate",
        title=f"Conversion Rate by Device Type - {selected_variant}",
        template="plotly_dark"
    )

    device_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e5e7eb"
    )

    seg_col1.plotly_chart(
        channel_chart,
        use_container_width=True
    )

    seg_col2.plotly_chart(
        device_chart,
        use_container_width=True
    )

    with st.expander("View segment tables"):
        st.subheader("Channel Performance")
        st.dataframe(channel_df, use_container_width=True)

        st.subheader("Device Performance")
        st.dataframe(device_df, use_container_width=True)

# =========================================================
# RETENTION TAB
# =========================================================
# Visualizes weekly cohort retention to evaluate user stickiness
# and post-signup engagement quality.

with tab5:
    st.markdown('<div class="section-title">Retention Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Weekly cohort retention view for product engagement monitoring.</div>', unsafe_allow_html=True)

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
        title=f"Weekly Cohort Retention - {selected_variant}",
        template="plotly_dark"
    )

    retention_heatmap.update_layout(
        height=550,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e5e7eb"
    )

    st.plotly_chart(
        retention_heatmap,
        use_container_width=True
    )

# =========================================================
# AI COPILOT TAB
# =========================================================
# Combines deterministic analytics lookup with LLM-powered
# strategic interpretation.
#
# The rule-based assistant returns direct metric answers.
# The LLM assistant uses structured analytics context to
# generate executive-style recommendations.

with tab6:
    st.markdown(
        """
        <div class="copilot-card">
            <div class="copilot-badge">AI PRODUCT INTELLIGENCE</div>
            <div class="section-title" style="margin-top:0px;">
                AI Product Analytics Copilot
            </div>
            <div class="section-subtitle">
                Ask product, experimentation, funnel, retention, and growth questions using rule-based analytics plus LLM-powered executive interpretation.
            </div>
            <div>
                <span class="prompt-chip">Why is the experiment underperforming?</span>
                <span class="prompt-chip">What should product teams focus on?</span>
                <span class="prompt-chip">Summarize funnel performance</span>
                <span class="prompt-chip">What are the biggest retention risks?</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    user_query = st.text_input(
        "Ask a product analytics question",
        placeholder="Example: What happened in the experiment?"
    )
    
    # Rule-based analytics assistant for deterministic metric lookup.
    if user_query:
        response = answer_query(user_query)

        if hasattr(response, "to_dict"):
            st.dataframe(
                response,
                use_container_width=True
            )
        else:
            st.info(response)

    llm_query = st.text_area(
        "Ask strategic analytics questions",
        placeholder="Example: Why is the experiment underperforming?"
    )
    
    # LLM-powered executive insight generation.
    # Numeric metrics are computed outside the LLM and injected
    # as structured context to reduce hallucination risk.
    if st.button("Generate Executive AI Insight"):

        if not llm_query.strip():
            st.warning("Enter a question before generating an insight.")
        else:
            with st.spinner("Generating executive insight..."):

                llm_response = generate_llm_response(
                    llm_query,
                    analytics_context
                )

                st.success(llm_response)

# =========================================================
# PLATFORM ARCHITECTURE FOOTER
# =========================================================
# Summarizes the technical and business scope of the platform
# for reviewers, recruiters, and stakeholders.

footer_html = """
<div class="footer-panel">

<div class="footer-title">
Platform Architecture
</div>

<div class="footer-grid">

<div class="footer-card">
<div class="footer-label">Analytics Stack</div>
<div class="footer-text">
PostgreSQL · Pandas · Plotly · Streamlit · Scikit-learn
</div>
</div>

<div class="footer-card">
<div class="footer-label">ML Capabilities</div>
<div class="footer-text">
A/B Testing · Forecasting · Isolation Forest · Cohort Retention · LLM Insights
</div>
</div>

<div class="footer-card">
<div class="footer-label">Business Focus</div>
<div class="footer-text">
Growth Analytics · Product Experimentation · Executive Decision Support
</div>
</div>

<div class="footer-card">
<div class="footer-label">Operational Scope</div>
<div class="footer-text">
Funnel Intelligence · Segmentation · Forecast Monitoring · Strategic Recommendations
</div>
</div>

</div>

</div>
"""

st.markdown(footer_html, unsafe_allow_html=True)