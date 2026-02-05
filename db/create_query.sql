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
        REFERENCES field(id) ON DELETE CASCADE
    CONSTRAINT uq_soil_measurement UNIQUE (ts, sensor_zone, water_content, field_id)
);

CREATE TABLE irrigation (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    ts TIMESTAMP NOT NULL,
    water_volume DOUBLE NOT NULL,
    field_id INTEGER NOT NULL,
    CONSTRAINT fk_irrigation_field FOREIGN KEY (field_id)
        REFERENCES field(id) ON DELETE CASCADE
    CONSTRAINT uq_irrigation UNIQUE (ts, water_volume, field_id)
);

CREATE TABLE lai (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    ts TIMESTAMP NOT NULL,
    lai DOUBLE NOT NULL,
    field_id INTEGER NOT NULL,
    CONSTRAINT fk_lai_field FOREIGN KEY (field_id)
        REFERENCES field(id) ON DELETE CASCADE
    CONSTRAINT uq_lai UNIQUE (ts, lai, field_id)
);

INSERT INTO field (id, crop_type, ir_mode) 
VALUES
    (5, 'ICBA', 'ai-Sensor'),
    (11, 'Titicaca', 'ai-Sensor'),
    (30, 'ICBA', 'ai-Sensor'),
    (32, 'Titicaca','ai-Sensor'),
    (52, 'Titicaca','ai-Sensor'),
    (54, 'ICBA', 'ai-Sensor');

INSERT INTO lai (ts, lai, field_id) 
VALUES
    ('2026-01-03 16:00:00', 0.0, 5),
    ('2026-01-03 16:00:00', 0.0, 11),
    ('2026-01-03 16:00:00', 0.0, 30),
    ('2026-01-03 16:00:00', 0.0, 32),
    ('2026-01-03 16:00:00', 0.0, 52),
    ('2026-01-03 16:00:00', 0.0, 54);