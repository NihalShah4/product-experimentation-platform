import pandas as pd
from sqlalchemy import create_engine


DB_PASSWORD = "admin"

engine = create_engine(
    f"postgresql://postgres:{DB_PASSWORD}@localhost:5432/product_analytics"
)


def get_retention_data():

    query = """
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