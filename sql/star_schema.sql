-- Star Schema for Fitbit Wellness Analytics

-- Dimension: User
CREATE TABLE IF NOT EXISTS dim_user (
    user_id VARCHAR(50) PRIMARY KEY,
    -- In a real scenario, we might have age, gender, etc.
    -- For this dataset, we only have ID, so this is a degenerate dimension or just a list of users.
    first_seen_date DATE
);

-- Dimension: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY, -- Format YYYYMMDD
    full_date DATE,
    day_name VARCHAR(10),
    day_of_week INT,
    month_name VARCHAR(10),
    month INT,
    year INT,
    is_weekend BOOLEAN
);

-- Fact: Daily Activity
CREATE TABLE IF NOT EXISTS fact_daily_activity (
    activity_id VARCHAR(100) PRIMARY KEY, -- Composite: user_id + date_key
    user_id VARCHAR(50),
    date_key INT,
    total_steps INT,
    total_distance FLOAT,
    tracker_distance FLOAT,
    logged_activities_distance FLOAT,
    very_active_distance FLOAT,
    moderately_active_distance FLOAT,
    light_active_distance FLOAT,
    sedentary_active_distance FLOAT,
    very_active_minutes INT,
    fairly_active_minutes INT,
    lightly_active_minutes INT,
    sedentary_minutes INT,
    calories FLOAT,
    FOREIGN KEY (user_id) REFERENCES dim_user(user_id),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

-- Fact: Sleep
CREATE TABLE IF NOT EXISTS fact_sleep (
    sleep_id VARCHAR(100) PRIMARY KEY, -- Composite: user_id + date_key
    user_id VARCHAR(50),
    date_key INT,
    total_sleep_records INT,
    total_minutes_asleep INT,
    total_time_in_bed INT,
    FOREIGN KEY (user_id) REFERENCES dim_user(user_id),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

-- KPI Table: Daily Wellness Score
CREATE TABLE IF NOT EXISTS fact_wellness_kpi (
    user_id VARCHAR(50),
    date_key INT,
    wellness_score FLOAT, -- Calculated: (steps/10000 * 0.5) + (sleep_hours/8 * 0.5) * 100
    activity_level VARCHAR(20), -- Sedentary, Active, Highly Active
    FOREIGN KEY (user_id) REFERENCES dim_user(user_id),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);
