"""
retention_analysis.py

Purpose:
Computes cohort retention analytics for the
Product Intelligence Platform.

Core Responsibilities:
- weekly cohort construction
- retention tracking
- engagement persistence analysis
- cohort heatmap support

Business Context:
Retention is one of the most important product metrics.

Strong acquisition without retention often indicates:
- weak onboarding
- poor product-market fit
- low feature adoption
- unsustainable growth

This module helps visualize:
- user engagement persistence
- cohort decay patterns
- long-term product stickiness
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
# COHORT RETENTION ANALYSIS
# =========================================================

def get_retention_data():
    """
    Computes weekly cohort retention metrics.

    Retention logic:
    - users are grouped by signup week
    - activity is tracked across future weeks
    - retention rate is calculated relative to
      original cohort size

    Returns:
        pandas.DataFrame:
            signup_week
            weeks_since_signup
            retention_rate
    """

    query = """
    WITH cohort_size AS (

        -- ================================================
        -- INITIAL COHORT SIZE
        -- ================================================
        --
        -- Defines the baseline number of users
        -- entering each weekly cohort.

        SELECT
            DATE_TRUNC('week', signup_date)::date AS signup_week,

            COUNT(DISTINCT user_id) AS cohort_users

        FROM users

        GROUP BY DATE_TRUNC('week', signup_date)::date
    ),

    user_activity AS (

        -- ================================================
        -- USER ACTIVITY RELATIVE TO SIGNUP
        -- ================================================
        --
        -- Computes how many weeks after signup
        -- each user remained active.

        SELECT
            u.user_id,

            DATE_TRUNC(
                'week',
                u.signup_date
            )::date AS signup_week,

            e.event_date,

            FLOOR(
                (e.event_date - u.signup_date) / 7
            ) AS weeks_since_signup

        FROM users u

        JOIN events e
            ON u.user_id = e.user_id
    ),

    retention_counts AS (

        -- ================================================
        -- ACTIVE USERS BY COHORT + WEEK
        -- ================================================

        SELECT
            signup_week,
            weeks_since_signup,

            COUNT(DISTINCT user_id) AS active_users

        FROM user_activity

        -- Restrict retention horizon to first 8 weeks
        WHERE weeks_since_signup BETWEEN 0 AND 8

        GROUP BY
            signup_week,
            weeks_since_signup
    )

    -- ====================================================
    -- FINAL RETENTION OUTPUT
    -- ====================================================

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

    ORDER BY
        r.signup_week,
        r.weeks_since_signup
    """

    return pd.read_sql(query, engine)