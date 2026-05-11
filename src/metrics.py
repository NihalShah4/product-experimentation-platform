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
    
def get_conversion_by_channel():

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


def get_conversion_by_device():

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