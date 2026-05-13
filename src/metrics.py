"""
metrics.py

Purpose:
Central analytics computation layer for the
Product Intelligence Platform.

Responsibilities:
- DAU computation
- conversion metrics
- funnel analytics
- acquisition segmentation
- device segmentation
- funnel conversion analysis

Design Philosophy:
This module intentionally centralizes analytical
queries to create:
- reusable metric definitions
- maintainable SQL logic
- dashboard consistency
- cleaner architecture

Technology Stack:
- PostgreSQL
- pandas
- SQLAlchemy
"""

import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


# =========================================================
# DATABASE CONNECTION
# =========================================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

# =========================================================
# DAILY ACTIVE USERS (DAU)
# =========================================================

def get_daily_active_users():
    """
    Computes Daily Active Users (DAU).

    DAU is a foundational product health metric used
    for:
    - engagement tracking
    - anomaly detection
    - forecasting
    - operational monitoring

    Returns:
        pandas.DataFrame
    """

    query = """
    SELECT
        event_date,
        COUNT(DISTINCT user_id) AS dau
    FROM events
    GROUP BY event_date
    ORDER BY event_date
    """

    return pd.read_sql(query, engine)


# =========================================================
# PLATFORM CONVERSION RATE
# =========================================================

def get_conversion_rate():
    """
    Computes overall platform conversion rate.

    Conversion is defined as:
    purchase sessions / total sessions

    Returns:
        pandas.DataFrame
    """

    query = """
    WITH sessions AS (

        -- ================================================
        -- Baseline sessions
        -- ================================================

        SELECT DISTINCT session_id
        FROM events
        WHERE event_type = 'session_start'
    ),

    purchases AS (

        -- ================================================
        -- Converted sessions
        -- ================================================

        SELECT DISTINCT session_id
        FROM events
        WHERE event_type = 'purchase'
    )

    SELECT
        ROUND(
            COUNT(DISTINCT purchases.session_id)::numeric
            /
            COUNT(DISTINCT sessions.session_id),
            4
        ) AS conversion_rate

    FROM sessions

    LEFT JOIN purchases
        ON sessions.session_id = purchases.session_id
    """

    return pd.read_sql(query, engine)


# =========================================================
# FUNNEL EVENT DISTRIBUTION
# =========================================================

def get_funnel_metrics():
    """
    Computes event distribution across the
    product funnel.

    Used for:
    - funnel visualization
    - drop-off monitoring
    - product engagement analysis

    Returns:
        pandas.DataFrame
    """

    query = """
    SELECT
        event_type,
        COUNT(*) AS total_events
    FROM events
    GROUP BY event_type
    ORDER BY total_events DESC
    """

    return pd.read_sql(query, engine)


# =========================================================
# CONVERSION BY ACQUISITION CHANNEL
# =========================================================

def get_conversion_by_channel():
    """
    Computes conversion performance across
    acquisition channels.

    Used for:
    - marketing analytics
    - growth prioritization
    - channel optimization

    Returns:
        pandas.DataFrame
    """

    query = """
    WITH sessions AS (

        SELECT
            u.acquisition_channel,
            e.session_id

        FROM events e

        JOIN users u
            ON e.user_id = u.user_id

        WHERE e.event_type = 'session_start'
    ),

    purchases AS (

        SELECT DISTINCT session_id
        FROM events
        WHERE event_type = 'purchase'
    )

    SELECT
        s.acquisition_channel,

        COUNT(DISTINCT s.session_id) AS total_sessions,

        COUNT(DISTINCT p.session_id) AS purchases,

        ROUND(
            COUNT(DISTINCT p.session_id)::numeric
            /
            COUNT(DISTINCT s.session_id),
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
# CONVERSION BY DEVICE TYPE
# =========================================================

def get_conversion_by_device():
    """
    Computes conversion performance by device segment.

    Used for:
    - UX optimization
    - responsive design analysis
    - device-specific experimentation

    Returns:
        pandas.DataFrame
    """

    query = """
    WITH sessions AS (

        SELECT
            u.device_type,
            e.session_id

        FROM events e

        JOIN users u
            ON e.user_id = u.user_id

        WHERE e.event_type = 'session_start'
    ),

    purchases AS (

        SELECT DISTINCT session_id
        FROM events
        WHERE event_type = 'purchase'
    )

    SELECT
        s.device_type,

        COUNT(DISTINCT s.session_id) AS total_sessions,

        COUNT(DISTINCT p.session_id) AS purchases,

        ROUND(
            COUNT(DISTINCT p.session_id)::numeric
            /
            COUNT(DISTINCT s.session_id),
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
# FUNNEL CONVERSION ANALYSIS
# =========================================================

def get_funnel_conversion():
    """
    Computes funnel conversion progression from
    session start through purchase.

    Outputs:
    - conversion_from_start
    - dropoff_from_start

    Used for:
    - funnel optimization
    - checkout analysis
    - UX diagnostics
    - product drop-off monitoring

    Returns:
        pandas.DataFrame
    """

    query = """
    WITH funnel AS (

        SELECT
            event_type,
            COUNT(DISTINCT session_id) AS sessions

        FROM events

        WHERE event_type IN (
            'session_start',
            'view_product',
            'add_to_cart',
            'purchase'
        )

        GROUP BY event_type
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

    # =====================================================
    # BASELINE FUNNEL STEP
    # =====================================================
    #
    # session_start is treated as the baseline
    # denominator for funnel conversion analysis.

    baseline = df["sessions"].iloc[0]

    # =====================================================
    # CONVERSION FROM FUNNEL ENTRY
    # =====================================================

    df["conversion_from_start"] = (
        df["sessions"] / baseline
    ).round(4)

    # =====================================================
    # DROPOFF FROM FUNNEL ENTRY
    # =====================================================

    df["dropoff_from_start"] = (
        1 - df["conversion_from_start"]
    ).round(4)

    return df