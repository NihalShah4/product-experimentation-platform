"""
main.py

Purpose:
Provides a lightweight FastAPI service layer for the
Product Intelligence Platform.

Current Responsibilities:
- API health monitoring
- platform availability validation
- future backend extensibility

Why FastAPI Exists Here:
The main dashboard currently runs through Streamlit, but
this API layer demonstrates backend extensibility and
production-oriented architecture thinking.

This creates a clearer separation between:
- presentation layer
- analytics layer
- backend service layer

Future Expansion Possibilities:
- metrics endpoints
- experiment APIs
- retention APIs
- authentication
- scheduled jobs
- orchestration
- model-serving endpoints
- external integrations
"""

from fastapi import FastAPI


# =========================================================
# FASTAPI APPLICATION INITIALIZATION
# =========================================================
#
# FastAPI is used as a lightweight backend service layer.
#
# The API currently exposes:
# - root endpoint
# - health check endpoint
#
# Additional analytics endpoints can be added later.

app = FastAPI(
    title="Product Experimentation Platform",

    description=(
        "API for product analytics, experimentation, "
        "and KPI monitoring."
    ),

    version="0.1.0",
)


# =========================================================
# ROOT ENDPOINT
# =========================================================
#
# Simple platform verification endpoint.

@app.get("/")
def home():

    return {
        "message": "Product Experimentation Platform API"
    }


# =========================================================
# HEALTH CHECK ENDPOINT
# =========================================================
#
# Used for:
# - deployment monitoring
# - uptime verification
# - orchestration health checks
# - infrastructure validation

@app.get("/health")
def health_check():

    return {
        "status": "running"
    }