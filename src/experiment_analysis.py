import pandas as pd
from sqlalchemy import create_engine
from scipy.stats import chi2_contingency


DB_PASSWORD = "admin"

engine = create_engine(
    f"postgresql://postgres:{DB_PASSWORD}@localhost:5432/product_analytics"
)


def get_experiment_results():

    query = """
    WITH sessions AS (
        SELECT
            variant,
            COUNT(DISTINCT session_id) AS total_sessions
        FROM events
        WHERE event_type = 'session_start'
        GROUP BY variant
    ),

    purchases AS (
        SELECT
            variant,
            COUNT(DISTINCT session_id) AS purchases
        FROM events
        WHERE event_type = 'purchase'
        GROUP BY variant
    )

    SELECT
        s.variant,
        s.total_sessions,
        COALESCE(p.purchases, 0) AS purchases,
        ROUND(
            COALESCE(p.purchases, 0)::numeric
            /
            s.total_sessions,
            4
        ) AS conversion_rate
    FROM sessions s
    LEFT JOIN purchases p
        ON s.variant = p.variant
    """

    return pd.read_sql(query, engine)


def run_chi_square_test(results_df):

    control = results_df[
        results_df["variant"] == "control"
    ].iloc[0]

    treatment = results_df[
        results_df["variant"] == "treatment"
    ].iloc[0]

    contingency_table = [
        [
            control["purchases"],
            control["total_sessions"] - control["purchases"]
        ],
        [
            treatment["purchases"],
            treatment["total_sessions"] - treatment["purchases"]
        ]
    ]

    chi2, p_value, _, _ = chi2_contingency(
        contingency_table
    )

    return round(p_value, 6)