CREATE DATABASE IF NOT EXISTS irrigation_db;
USE irrigation_db;

CREATE TABLE field (
    id INT NOT NULL PRIMARY KEY,
    crop_type VARCHAR(100) NOT NULL,
    ir_mode VARCHAR(50) NOT NULL
);

CREATE TABLE soil_moisture (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    ts TIMESTAMP NOT NULL,
    sensor_zone VARCHAR(5) NOT NULL,
    water_content DOUBLE NOT NULL,
    field_id INT NOT NULL,
    CONSTRAINT fk_soil_field FOREIGN KEY (field_id)
        REFERENCES field(id) ON DELETE CASCADE,
    CONSTRAINT uq_soil_measurement UNIQUE (ts, sensor_zone, field_id)
);

CREATE TABLE irrigation (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    ts TIMESTAMP NOT NULL,
    water_volume DOUBLE NOT NULL,
    field_id INTEGER NOT NULL,
    CONSTRAINT fk_irrigation_field FOREIGN KEY (field_id)
        REFERENCES field(id) ON DELETE CASCADE,
    CONSTRAINT uq_irrigation_event UNIQUE (ts, field_id)
);

CREATE TABLE lai (
    iid BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    ts TIMESTAMP NOT NULL,
    lai DOUBLE NOT NULL,
    field_id INTEGER NOT NULL,
    CONSTRAINT fk_lai_field FOREIGN KEY (field_id)
        REFERENCES field(id) ON DELETE CASCADE,
    CONSTRAINT uq_lai_measurement UNIQUE (ts, field_id)
);

