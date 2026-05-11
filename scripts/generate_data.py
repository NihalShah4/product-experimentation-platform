import random
import uuid
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import create_engine


DB_PASSWORD = "admin"

engine = create_engine(
    f"postgresql://postgres:{DB_PASSWORD}@localhost:5432/product_analytics"
)

random.seed(42)

countries = ["USA", "Canada", "India", "UK", "Germany"]
channels = ["organic", "paid_search", "social", "referral", "email"]
devices = ["desktop", "mobile", "tablet"]

start_date = datetime(2025, 1, 1)
num_users = 5000

users = []
events = []

for user_id in range(1, num_users + 1):
    signup_date = start_date + timedelta(days=random.randint(0, 89))
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

    active_days = random.randint(1, 20)

    for _ in range(active_days):
        event_date = signup_date + timedelta(days=random.randint(0, 60))
        session_id = str(uuid.uuid4())

        events.append({
            "user_id": user_id,
            "event_date": event_date.date(),
            "event_type": "session_start",
            "session_id": session_id,
            "experiment_id": 1,
            "variant": random.choice(["control", "treatment"])
        })

        if random.random() < 0.65:
            events.append({
                "user_id": user_id,
                "event_date": event_date.date(),
                "event_type": "view_product",
                "session_id": session_id,
                "experiment_id": 1,
                "variant": random.choice(["control", "treatment"])
            })

        if random.random() < 0.35:
            events.append({
                "user_id": user_id,
                "event_date": event_date.date(),
                "event_type": "add_to_cart",
                "session_id": session_id,
                "experiment_id": 1,
                "variant": random.choice(["control", "treatment"])
            })

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
                "variant": random.choice(["control", "treatment"])
            })


users_df = pd.DataFrame(users)
events_df = pd.DataFrame(events)

experiments_df = pd.DataFrame([{
    "experiment_id": 1,
    "experiment_name": "checkout_page_redesign",
    "variant": "control",
    "start_date": datetime(2025, 1, 1).date(),
    "end_date": datetime(2025, 3, 31).date()
}, {
    "experiment_id": 2,
    "experiment_name": "checkout_page_redesign",
    "variant": "treatment",
    "start_date": datetime(2025, 1, 1).date(),
    "end_date": datetime(2025, 3, 31).date()
}])

users_df.to_sql("users", engine, if_exists="append", index=False)
experiments_df.to_sql("experiments", engine, if_exists="append", index=False)
events_df.to_sql("events", engine, if_exists="append", index=False)

print("Data generation complete")
print(f"Users inserted: {len(users_df)}")
print(f"Events inserted: {len(events_df)}")