import random
import uuid
from datetime import datetime, timedelta

import pandas as pd

from src.metrics import engine


def generate_simulation_data(
    max_users,
    date_range_days
):
    """
    Generates synthetic product analytics data with guardrails.

    User-selected max_users is treated as an upper bound.
    Actual generated users are randomized between 90% and 100%
    of the selected value to simulate realistic variation.
    """

    random.seed()

    actual_users = random.randint(
        int(max_users * 0.90),
        max_users
    )

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

    for user_id in range(1, actual_users + 1):

        signup_date = start_date + timedelta(
            days=random.randint(0, date_range_days - 1)
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

        active_days = random.randint(
            1,
            min(20, date_range_days)
        )

        for _ in range(active_days):

            event_date = signup_date + timedelta(
                days=random.randint(0, date_range_days)
            )

            session_id = str(uuid.uuid4())

            variant = random.choice(
                ["control", "treatment"]
            )

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

            conversion_prob = 0.08

            if channel == "email":
                conversion_prob += 0.03

            if device == "desktop":
                conversion_prob += 0.02

            if variant == "treatment":
                conversion_prob -= 0.002

            if random.random() < conversion_prob:
                events.append({
                    "user_id": user_id,
                    "event_date": event_date.date(),
                    "event_type": "purchase",
                    "session_id": session_id,
                    "experiment_id": 1,
                    "variant": variant
                })

    users_df = pd.DataFrame(users)
    events_df = pd.DataFrame(events)

    experiments_df = pd.DataFrame([
        {
            "experiment_id": 1,
            "experiment_name": "checkout_page_redesign",
            "variant": "control",
            "start_date": start_date.date(),
            "end_date": (
                start_date + timedelta(days=date_range_days)
            ).date()
        },
        {
            "experiment_id": 2,
            "experiment_name": "checkout_page_redesign",
            "variant": "treatment",
            "start_date": start_date.date(),
            "end_date": (
                start_date + timedelta(days=date_range_days)
            ).date()
        }
    ])

    with engine.begin() as connection:
        connection.exec_driver_sql(
            "TRUNCATE TABLE events, experiments, users RESTART IDENTITY CASCADE;"
        )

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

    return {
        "requested_max_users": max_users,
        "actual_users": actual_users,
        "events_generated": len(events_df),
        "date_range_days": date_range_days
    }