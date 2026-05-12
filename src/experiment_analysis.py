"""
experiment_analysis.py

Purpose:
Provides experiment analytics and statistical testing
for A/B product experimentation.

Core Responsibilities:
- compute conversion metrics
- compare control vs treatment performance
- run statistical significance testing

Statistical Method:
- Chi-Square Test of Independence

Business Context:
This module simulates how product analytics teams
evaluate whether an experiment should be rolled out
to production users.
"""

import os

import pandas as pd
from dotenv import load_dotenv
from scipy.stats import chi2_contingency
from sqlalchemy import create_engine


# =========================================================
# DATABASE CONNECTION
# =========================================================

load_dotenv()

DB_PASSWORD = os.getenv("DB_PASSWORD")

engine = create_engine(
    f"postgresql://postgres:{DB_PASSWORD}@localhost:5432/product_analytics"
)


# =========================================================
# EXPERIMENT RESULT AGGREGATION
# =========================================================

def get_experiment_results():
    """
    Computes experiment-level conversion performance.

    Returns:
        pandas.DataFrame:
            variant
            total_sessions
            purchases
            conversion_rate
    """

    query = """
    WITH sessions AS (

        -- ================================================
        -- Session baseline for each experiment variant
        -- ================================================

        SELECT
            variant,
            COUNT(DISTINCT session_id) AS total_sessions
        FROM events
        WHERE event_type = 'session_start'
        GROUP BY variant
    ),

    purchases AS (

        -- ================================================
        -- Purchase conversions for each experiment variant
        -- ================================================

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

        COALESCE(
            p.purchases,
            0
        ) AS purchases,

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


# =========================================================
# CHI-SQUARE STATISTICAL TEST
# =========================================================

def run_chi_square_test(results_df):
    """
    Performs a Chi-Square Test of Independence to determine
    whether conversion differences between control and
    treatment are statistically significant.

    Why Chi-Square?
    - appropriate for categorical conversion outcomes
    - common in experimentation systems
    - interpretable for business stakeholders

    Parameters:
        results_df (pandas.DataFrame):
            Experiment summary dataframe

    Returns:
        float:
            p-value rounded to 6 decimal places
    """

    # =====================================================
    # EXTRACT CONTROL + TREATMENT GROUPS
    # =====================================================

    control = results_df[
        results_df["variant"] == "control"
    ].iloc[0]

    treatment = results_df[
        results_df["variant"] == "treatment"
    ].iloc[0]

    # =====================================================
    # BUILD CONTINGENCY TABLE
    # =====================================================
    #
    # Table structure:
    #
    #                Converted   Not Converted
    # Control
    # Treatment
    #
    # Used by Chi-Square statistical test.

    contingency_table = [
        [
            control["purchases"],
            control["total_sessions"]
            - control["purchases"]
        ],
        [
            treatment["purchases"],
            treatment["total_sessions"]
            - treatment["purchases"]
        ]
    ]

    # =====================================================
    # RUN CHI-SQUARE TEST
    # =====================================================

    chi2, p_value, _, _ = chi2_contingency(
        contingency_table
    )

    return round(p_value, 6)