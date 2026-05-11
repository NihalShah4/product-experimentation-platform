DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS experiments;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    signup_date DATE NOT NULL,
    country VARCHAR(50),
    acquisition_channel VARCHAR(50),
    device_type VARCHAR(50)
);

CREATE TABLE experiments (
    experiment_id SERIAL PRIMARY KEY,
    experiment_name VARCHAR(100),
    variant VARCHAR(20),
    start_date DATE,
    end_date DATE
);

CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    event_date DATE NOT NULL,
    event_type VARCHAR(50),
    session_id VARCHAR(100),
    experiment_id INT REFERENCES experiments(experiment_id),
    variant VARCHAR(20)
);