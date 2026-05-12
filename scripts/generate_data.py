"""
generate_data.py

Initial synthetic data generator for the Product Intelligence Platform.

Purpose:
- Creates synthetic users, experiments, and product events
- Inserts generated records into PostgreSQL
- Provides a reproducible baseline dataset for local development

This script is intended for initial database population.
The interactive dashboard uses simulation_engine.py for guarded regeneration.
"""

import os
import random
import uuid
from datetime import datetime, timedelta

import pandas as pd
from dotenv import load_dotenv
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
# SIMULATION CONFIGURATION
# =========================================================

random.seed(42)

COUNTRIES = ["USA", "Canada", "India", "UK", "Germany"]
CHANNELS = ["organic", "paid_search", "social", "referral", "email"]
DEVICES = ["desktop", "mobile", "tablet"]

START_DATE = datetime(2025, 1, 1)
NUM_USERS = 5000


# =========================================================
# SYNTHETIC USER + EVENT GENERATION
# =========================================================

users = []
events = []

for user_id in range(1, NUM_USERS + 1):

    signup_date = START_DATE + timedelta(
        days=random.randint(0, 89)
    )

    country = random.choice(COUNTRIES)
    channel = random.choice(CHANNELS)
    device = random.choice(DEVICES)

    users.append({
        "user_id": user_id,
        "signup_date": signup_date.date(),
        "country": country,
        "acquisition_channel": channel,
        "device_type": device
    })

    # Each user is assigned multiple active days to create
    # repeat engagement and retention behavior.
    active_days = random.randint(1, 20)

    for _ in range(active_days):

        event_date = signup_date + timedelta(
            days=random.randint(0, 60)
        )

        session_id = str(uuid.uuid4())

        # Assign one experiment variant per session.
        variant = random.choice(["control", "treatment"])

        events.append({
            "user_id": user_id,
            "event_date": event_date.date(),
            "event_type": "session_start",
            "session_id": session_id,
            "experiment_id": 1,
            "variant": variant
        })

        if random.random() < 0.65:
            events.append({
                "user_id": user_id,
                "event_date": event_date.date(),
                "event_type": "view_product",
                "session_id": session_id,
                "experiment_id": 1,
                "variant": variant
            })

        if random.random() < 0.35:
            events.append({
                "user_id": user_id,
                "event_date": event_date.date(),
                "event_type": "add_to_cart",
                "session_id": session_id,
                "experiment_id": 1,
                "variant": variant
            })

        # Conversion probability is intentionally simple and explainable:
        # - email users are modeled as higher-intent traffic
        # - desktop users are modeled as slightly more conversion-prone
        conversion_prob = 0.08

        if channel == "email":
            conversion_prob += 0.03

        if device == "desktop":
            conversion_prob += 0.02

        if random.random() < conversion_prob:
            events.append({
                "user_id": user_id,
                "event_date": event_date.date(),
                "event_type": "purchase",
                "session_id": session_id,
                "experiment_id": 1,
                "variant": variant
            })


# =========================================================
# DATAFRAME PREPARATION
# =========================================================

users_df = pd.DataFrame(users)
events_df = pd.DataFrame(events)

experiments_df = pd.DataFrame([
    {
        "experiment_id": 1,
        "experiment_name": "checkout_page_redesign",
        "variant": "control",
        "start_date": datetime(2025, 1, 1).date(),
        "end_date": datetime(2025, 3, 31).date()
    },
    {
        "experiment_id": 2,
        "experiment_name": "checkout_page_redesign",
        "variant": "treatment",
        "start_date": datetime(2025, 1, 1).date(),
        "end_date": datetime(2025, 3, 31).date()
    }
])


# =========================================================
# DATABASE INSERTION
# =========================================================

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


# =========================================================
# VALIDATION OUTPUT
# =========================================================

print("Data generation complete")
print(f"Users inserted: {len(users_df)}")
print(f"Experiments inserted: {len(experiments_df)}")
print(f"Events inserted: {len(events_df)}")