/*
=========================================================
PRODUCT INTELLIGENCE PLATFORM - DATABASE SCHEMA
=========================================================

Purpose:
Defines the PostgreSQL schema used by the Product
Intelligence Platform.

The schema is intentionally lightweight and optimized
for:
- experimentation analytics
- funnel analysis
- retention analysis
- segmentation
- forecasting
- anomaly detection

Tables:
1. users
2. experiments
3. events

Design Philosophy:
- simple relational structure
- analytics-friendly joins
- explainable product-event modeling
- synthetic experimentation support
=========================================================
*/


-- =====================================================
-- CLEAN RESET
-- =====================================================
-- Existing tables are dropped in dependency order
-- to support repeated synthetic data generation.

DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS experiments;
DROP TABLE IF EXISTS users;


-- =====================================================
-- USERS TABLE
-- =====================================================
-- Stores user-level metadata used for:
-- - segmentation
-- - retention analysis
-- - acquisition analysis
-- - device analytics

CREATE TABLE users (

    -- Unique user identifier
    user_id SERIAL PRIMARY KEY,

    -- User signup date used for cohort analysis
    signup_date DATE NOT NULL,

    -- Geographic segmentation
    country VARCHAR(50),

    -- Marketing acquisition source
    acquisition_channel VARCHAR(50),

    -- Primary device category
    device_type VARCHAR(50)
);


-- =====================================================
-- EXPERIMENTS TABLE
-- =====================================================
-- Stores A/B experiment metadata.
--
-- Current implementation models:
-- - control variant
-- - treatment variant
--
-- This structure supports future expansion into:
-- - multi-variant experiments
-- - sequential testing
-- - rollout governance

CREATE TABLE experiments (

    -- Unique experiment identifier
    experiment_id SERIAL PRIMARY KEY,

    -- Human-readable experiment name
    experiment_name VARCHAR(100),

    -- Experiment variant label
    variant VARCHAR(20),

    -- Experiment active period
    start_date DATE,
    end_date DATE
);


-- =====================================================
-- EVENTS TABLE
-- =====================================================
-- Central product-event fact table.
--
-- Stores behavioral analytics events used for:
-- - DAU computation
-- - funnel analytics
-- - conversion analysis
-- - forecasting
-- - anomaly detection
-- - retention analysis

CREATE TABLE events (

    -- Unique event identifier
    event_id SERIAL PRIMARY KEY,

    -- Foreign key to users table
    user_id INT REFERENCES users(user_id),

    -- Product interaction date
    event_date DATE NOT NULL,

    -- Product event type
    --
    -- Current supported events:
    -- - session_start
    -- - view_product
    -- - add_to_cart
    -- - purchase
    event_type VARCHAR(50),

    -- Session identifier used for funnel analysis
    session_id VARCHAR(100),

    -- Linked experiment reference
    experiment_id INT REFERENCES experiments(experiment_id),

    -- Experiment variant assigned to event
    variant VARCHAR(20)
);


/*
=========================================================
SCHEMA NOTES
=========================================================

1. The schema intentionally avoids excessive normalization
   to simplify analytical querying and dashboard latency.

2. Event-level variant assignment enables:
   - variant-level funnel analysis
   - segmented experimentation analysis
   - retention comparison
   - conversion attribution

3. This schema is optimized for:
   - PostgreSQL
   - pandas ingestion
   - Streamlit analytics rendering

4. Synthetic data generation is handled by:
   - generate_data.py
   - simulation_engine.py
=========================================================
*/