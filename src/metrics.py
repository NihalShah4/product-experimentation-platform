import pandas as pd
from sqlalchemy import create_engine


DB_PASSWORD = "admin"

engine = create_engine(
    f"postgresql://postgres:{DB_PASSWORD}@localhost:5432/product_analytics"
)


def get_daily_active_users():

    query = """
    SELECT
        event_date,
        COUNT(DISTINCT user_id) AS dau
    FROM events
    GROUP BY event_date
    ORDER BY event_date
    """

    return pd.read_sql(query, engine)


def get_conversion_rate():

    query = """
    WITH sessions AS (
        SELECT DISTINCT session_id
        FROM events
        WHERE event_type = 'session_start'
    ),

    purchases AS (
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


def get_funnel_metrics():

    query = """
    SELECT
        event_type,
        COUNT(*) AS total_events
    FROM events
    GROUP BY event_type
    ORDER BY total_events DESC
    """

    return pd.read_sql(query, engine)