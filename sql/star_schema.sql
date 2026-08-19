-- Star schema for hotel booking analytics.


CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE,
    year SMALLINT,
    quarter SMALLINT,
    month SMALLINT,
    month_name VARCHAR(10),
    week_number SMALLINT,
    day_of_month SMALLINT,
    day_of_week VARCHAR(10),
    is_weekend BOOLEAN
);

CREATE TABLE dim_hotel (
    hotel_key SMALLSERIAL PRIMARY KEY,
    hotel_name VARCHAR(50) UNIQUE
);

CREATE TABLE dim_customer_profile (
    profile_key SMALLSERIAL PRIMARY KEY,
    customer_type VARCHAR(20),
    is_repeated_guest BOOLEAN,
    deposit_type VARCHAR(20)
);

CREATE TABLE dim_country (
    country_key SMALLSERIAL PRIMARY KEY,
    country VARCHAR(20) UNIQUE
);

CREATE TABLE dim_meal (
    meal_key SMALLSERIAL PRIMARY KEY,
    meal VARCHAR(5) UNIQUE
);

CREATE TABLE dim_distribution_channel (
    channel_key SMALLSERIAL PRIMARY KEY,
    distribution_channel VARCHAR(30) UNIQUE
);

CREATE TABLE dim_market_segment (
    segment_key SMALLSERIAL PRIMARY KEY,
    market_segment VARCHAR(30) UNIQUE
);

CREATE TABLE fact_bookings (
    booking_sk BIGSERIAL PRIMARY KEY,
    hotel_key SMALLINT REFERENCES dim_hotel(hotel_key),
    arrival_date_key INTEGER REFERENCES dim_date(date_key),
    status_date_key INTEGER REFERENCES dim_date(date_key),
    profile_key SMALLINT REFERENCES dim_customer_profile(profile_key),
    country_key SMALLINT REFERENCES dim_country(country_key),
    meal_key SMALLINT REFERENCES dim_meal(meal_key),
    channel_key SMALLINT REFERENCES dim_distribution_channel(channel_key),
    segment_key SMALLINT REFERENCES dim_market_segment(segment_key),

    reserved_room_type VARCHAR(5),
    assigned_room_type VARCHAR(5),
    room_type_changed BOOLEAN,
    reservation_status VARCHAR(15),
    cancelled BOOLEAN,

    lead_time SMALLINT,
    stays_weekend_nights SMALLINT,
    stays_week_nights SMALLINT,
    total_nights SMALLINT,
    adults SMALLINT,
    children SMALLINT,
    babies SMALLINT,
    total_guests SMALLINT,
    adr NUMERIC(10,2),
    booking_changes SMALLINT,
    days_in_waiting_list SMALLINT,
    previous_cancellations SMALLINT,
    previous_bookings_not_canceled SMALLINT,
    agent SMALLINT,
    company SMALLINT,
    has_agent BOOLEAN,
    has_company BOOLEAN,
    required_car_parking_spaces SMALLINT,
    total_of_special_requests SMALLINT
);