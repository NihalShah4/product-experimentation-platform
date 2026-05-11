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
            signup_date,
            COUNT(DISTINCT user_id) AS cohort_users

        FROM users

        GROUP BY signup_date
    ),

    user_activity AS (

        SELECT
            u.user_id,
            u.signup_date,
            e.event_date,
            (e.event_date - u.signup_date) AS days_since_signup

        FROM users u

        JOIN events e
            ON u.user_id = e.user_id
    ),

    retention_counts AS (

        SELECT
            signup_date,
            days_since_signup,
            COUNT(DISTINCT user_id) AS active_users

        FROM user_activity

        WHERE days_since_signup BETWEEN 0 AND 30

        GROUP BY signup_date, days_since_signup
    )

    SELECT
        r.signup_date,
        r.days_since_signup,
        ROUND(
            r.active_users::numeric
            /
            c.cohort_users,
            4
        ) AS retention_rate

    FROM retention_counts r

    JOIN cohort_size c
        ON r.signup_date = c.signup_date

    ORDER BY r.signup_date, r.days_since_signup
    """

    return pd.read_sql(query, engine)