"""
simulation_engine.py

Purpose:
Provides guarded synthetic data generation for the
Product Intelligence Platform.

Core Responsibilities:
- generate synthetic users
- generate behavioral product events
- simulate experimentation traffic
- populate PostgreSQL dynamically
- support controlled simulation workflows

Design Philosophy:
This module intentionally demonstrates:
- analytics system simulation
- database write operations
- guardrail enforcement
- controlled randomness
- synthetic experimentation environments

Why Guardrails Matter:
The simulation system intentionally limits:
- user volume
- date range
- generation frequency

This mirrors real-world production safeguards where
unrestricted data generation could:
- overload infrastructure
- corrupt analytics environments
- create operational instability

Key Guardrail:
User-selected volume acts as an upper bound.
Actual generated volume is randomized between
90–100% of the selected cap to simulate realistic
traffic variability.
"""

import random
import uuid
from datetime import datetime, timedelta

import pandas as pd

from src.metrics import engine


# =========================================================
# SYNTHETIC DATA GENERATION ENGINE
# =========================================================

def generate_simulation_data(
    max_users,
    date_range_days
):
    """
    Generates guarded synthetic analytics data and
    inserts it into PostgreSQL.

    Parameters:
        max_users (int):
            Maximum user generation cap.

        date_range_days (int):
            Simulation time horizon.

    Returns:
        dict:
            requested_max_users
            actual_users
            events_generated
            date_range_days
    """

    # =====================================================
    # RANDOMIZED USER VOLUME
    # =====================================================
    #
    # The requested user count is intentionally treated
    # as a ceiling rather than an exact target.
    #
    # This creates more realistic simulation variance.

    random.seed()

    actual_users = random.randint(
        int(max_users * 0.90),
        max_users
    )

    # =====================================================
    # SYNTHETIC SEGMENT DEFINITIONS
    # =====================================================

    countries = [
        "USA",
        "Canada",
        "India",
        "UK",
        "Germany"
    ]

    channels = [
        "organic",
        "paid_search",
        "social",
        "referral",
        "email"
    ]

    devices = [
        "desktop",
        "mobile",
        "tablet"
    ]

    start_date = datetime(2025, 1, 1)

    users = []
    events = []

    # =====================================================
    # USER GENERATION LOOP
    # =====================================================

    for user_id in range(1, actual_users + 1):

        signup_date = start_date + timedelta(
            days=random.randint(
                0,
                date_range_days - 1
            )
        )

        country = random.choice(countries)
        channel = random.choice(channels)
        device = random.choice(devices)

        users.append({
            "user_id": user_id,
            "signup_date": signup_date.date(),
            "country": country,
            "acquisition_channel": channel,
            "device_type": device
        })

        # =================================================
        # USER ENGAGEMENT SIMULATION
        # =================================================
        #
        # Users are assigned multiple active days
        # to create retention + engagement behavior.

        active_days = random.randint(
            1,
            min(20, date_range_days)
        )

        for _ in range(active_days):

            event_date = signup_date + timedelta(
                days=random.randint(
                    0,
                    date_range_days
                )
            )

            session_id = str(uuid.uuid4())

            # =============================================
            # EXPERIMENT ASSIGNMENT
            # =============================================

            variant = random.choice(
                ["control", "treatment"]
            )

            # =============================================
            # SESSION START EVENT
            # =============================================

            events.append({
                "user_id": user_id,
                "event_date": event_date.date(),
                "event_type": "session_start",
                "session_id": session_id,
                "experiment_id": 1,
                "variant": variant
            })

            # =============================================
            # PRODUCT VIEW EVENT
            # =============================================

            if random.random() < 0.65:

                events.append({
                    "user_id": user_id,
                    "event_date": event_date.date(),
                    "event_type": "view_product",
                    "session_id": session_id,
                    "experiment_id": 1,
                    "variant": variant
                })

            # =============================================
            # ADD-TO-CART EVENT
            # =============================================

            if random.random() < 0.35:

                events.append({
                    "user_id": user_id,
                    "event_date": event_date.date(),
                    "event_type": "add_to_cart",
                    "session_id": session_id,
                    "experiment_id": 1,
                    "variant": variant
                })

            # =============================================
            # PURCHASE CONVERSION LOGIC
            # =============================================
            #
            # Synthetic business assumptions:
            #
            # - email traffic converts better
            # - desktop traffic converts better
            # - treatment variant slightly underperforms
            #
            # This creates meaningful analytical variation.

            conversion_prob = 0.08

            if channel == "email":
                conversion_prob += 0.03

            if device == "desktop":
                conversion_prob += 0.02

            if variant == "treatment":
                conversion_prob -= 0.002

            # =============================================
            # PURCHASE EVENT
            # =============================================

            if random.random() < conversion_prob:

                events.append({
                    "user_id": user_id,
                    "event_date": event_date.date(),
                    "event_type": "purchase",
                    "session_id": session_id,
                    "experiment_id": 1,
                    "variant": variant
                })

    # =====================================================
    # DATAFRAME CONVERSION
    # =====================================================

    users_df = pd.DataFrame(users)

    events_df = pd.DataFrame(events)

    # =====================================================
    # EXPERIMENT METADATA
    # =====================================================

    experiments_df = pd.DataFrame([
        {
            "experiment_id": 1,
            "experiment_name": "checkout_page_redesign",
            "variant": "control",
            "start_date": start_date.date(),
            "end_date": (
                start_date + timedelta(
                    days=date_range_days
                )
            ).date()
        },
        {
            "experiment_id": 2,
            "experiment_name": "checkout_page_redesign",
            "variant": "treatment",
            "start_date": start_date.date(),
            "end_date": (
                start_date + timedelta(
                    days=date_range_days
                )
            ).date()
        }
    ])

    # =====================================================
    # DATABASE RESET
    # =====================================================
    #
    # Existing synthetic records are removed before
    # new simulation insertion.
    #
    # CASCADE ensures dependent rows are safely removed.

    with engine.begin() as connection:

        connection.exec_driver_sql(
            """
            TRUNCATE TABLE
                events,
                experiments,
                users
            RESTART IDENTITY CASCADE;
            """
        )

    # =====================================================
    # DATABASE INSERTION
    # =====================================================

    users_df.to_sql(
        "users",
        engine,
        if_exists="append",
        index=False
    )

    experiments_df.to_sql(
        "experiments",
        engine,
        if_exists="append",
        index=False
    )

    events_df.to_sql(
        "events",
        engine,
        if_exists="append",
        index=False
    )

    # =====================================================
    # EXECUTION SUMMARY
    # =====================================================

    return {
        "requested_max_users": max_users,
        "actual_users": actual_users,
        "events_generated": len(events_df),
        "date_range_days": date_range_days
    }