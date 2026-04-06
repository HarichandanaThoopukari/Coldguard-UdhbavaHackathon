-- Cold Storage Temperature Monitoring System
-- Database Schema for SQLite

-- Storage Units Table
CREATE TABLE IF NOT EXISTS storage_units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    capacity_tons REAL,
    storage_type VARCHAR(50) DEFAULT 'Mixed',
    min_temp REAL DEFAULT -5.0,
    max_temp REAL DEFAULT 8.0,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Temperature Readings Table
CREATE TABLE IF NOT EXISTS temperature_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    storage_unit_id INTEGER NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    recorded_by VARCHAR(100),
    is_manual BOOLEAN DEFAULT 0,
    FOREIGN KEY (storage_unit_id) REFERENCES storage_units(id)
);

-- Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    storage_unit_id INTEGER NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    temperature_reading REAL,
    is_acknowledged BOOLEAN DEFAULT 0,
    acknowledged_by VARCHAR(100),
    acknowledged_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (storage_unit_id) REFERENCES storage_units(id)
);

-- Power Failures Table
CREATE TABLE IF NOT EXISTS power_failures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    storage_unit_id INTEGER NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    duration_minutes INTEGER,
    cause VARCHAR(200),
    notes TEXT,
    reported_by VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (storage_unit_id) REFERENCES storage_units(id)
);

-- Maintenance Logs Table
CREATE TABLE IF NOT EXISTS maintenance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    storage_unit_id INTEGER NOT NULL,
    maintenance_type VARCHAR(100) NOT NULL,
    description TEXT,
    performed_by VARCHAR(100) NOT NULL,
    performed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    next_maintenance_due DATETIME,
    cost REAL,
    status VARCHAR(50) DEFAULT 'Completed',
    FOREIGN KEY (storage_unit_id) REFERENCES storage_units(id)
);

-- Users Table (for future authentication)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    role VARCHAR(20) DEFAULT 'operator',
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Notification Settings Table
CREATE TABLE IF NOT EXISTS notification_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    storage_unit_id INTEGER,
    notify_high_temp BOOLEAN DEFAULT 1,
    notify_low_temp BOOLEAN DEFAULT 1,
    notify_power_failure BOOLEAN DEFAULT 1,
    notify_maintenance_due BOOLEAN DEFAULT 1,
    notification_method VARCHAR(20) DEFAULT 'sms',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (storage_unit_id) REFERENCES storage_units(id)
);

-- Daily Reports Table
CREATE TABLE IF NOT EXISTS daily_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    storage_unit_id INTEGER NOT NULL,
    report_date DATE NOT NULL,
    min_temp REAL,
    max_temp REAL,
    avg_temp REAL,
    total_readings INTEGER,
    alerts_count INTEGER DEFAULT 0,
    power_failures_count INTEGER DEFAULT 0,
    status VARCHAR(50),
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (storage_unit_id) REFERENCES storage_units(id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_temp_readings_unit ON temperature_readings(storage_unit_id);
CREATE INDEX IF NOT EXISTS idx_temp_readings_date ON temperature_readings(recorded_at);
CREATE INDEX IF NOT EXISTS idx_alerts_unit ON alerts(storage_unit_id);
CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at);
CREATE INDEX IF NOT EXISTS idx_power_failures_unit ON power_failures(storage_unit_id);

-- Insert sample data
INSERT INTO storage_units (name, location, capacity_tons, storage_type, min_temp, max_temp) VALUES
('Unit A - Main Potato Storage', 'Block A, Agra Road', 500, 'Potato', 2.0, 4.0),
('Unit B - Vegetable Cold Room', 'Block B, Near Market', 200, 'Vegetable', 0.0, 5.0),
('Unit C - Mixed Storage', 'Block C, Industrial Area', 350, 'Mixed', -2.0, 6.0),
('Unit D - Premium Fruit Storage', 'Block D, Highway Side', 150, 'Fruit', 1.0, 4.0);

INSERT INTO users (username, email, phone, role) VALUES
('admin', 'admin@coldstorage.com', '9876543210', 'admin'),
('operator1', 'operator1@coldstorage.com', '9876543211', 'operator'),
('manager', 'manager@coldstorage.com', '9876543212', 'manager');

-- Insert sample temperature readings (last 24 hours simulation)
INSERT INTO temperature_readings (storage_unit_id, temperature, humidity, recorded_at) VALUES
(1, 3.2, 85, datetime('now', '-23 hours')),
(1, 3.4, 84, datetime('now', '-22 hours')),
(1, 3.1, 86, datetime('now', '-21 hours')),
(1, 3.5, 85, datetime('now', '-20 hours')),
(1, 3.8, 84, datetime('now', '-19 hours')),
(1, 4.2, 83, datetime('now', '-18 hours')),
(1, 4.5, 82, datetime('now', '-17 hours')),
(1, 4.1, 83, datetime('now', '-16 hours')),
(1, 3.9, 84, datetime('now', '-15 hours')),
(1, 3.6, 85, datetime('now', '-14 hours')),
(1, 3.3, 86, datetime('now', '-13 hours')),
(1, 3.2, 86, datetime('now', '-12 hours')),
(1, 3.4, 85, datetime('now', '-11 hours')),
(1, 3.7, 84, datetime('now', '-10 hours')),
(1, 3.9, 84, datetime('now', '-9 hours')),
(1, 4.3, 83, datetime('now', '-8 hours')),
(1, 4.6, 82, datetime('now', '-7 hours')),
(1, 4.8, 81, datetime('now', '-6 hours')),
(1, 5.2, 80, datetime('now', '-5 hours')),
(1, 5.5, 79, datetime('now', '-4 hours')),
(1, 5.1, 80, datetime('now', '-3 hours')),
(1, 4.7, 81, datetime('now', '-2 hours')),
(1, 4.2, 82, datetime('now', '-1 hours')),
(1, 3.8, 84, datetime('now'));

-- Sample readings for other units
INSERT INTO temperature_readings (storage_unit_id, temperature, humidity, recorded_at) VALUES
(2, 2.5, 88, datetime('now', '-2 hours')),
(2, 2.8, 87, datetime('now', '-1 hours')),
(2, 2.6, 88, datetime('now')),
(3, 1.2, 82, datetime('now', '-2 hours')),
(3, 1.5, 81, datetime('now', '-1 hours')),
(3, 1.3, 82, datetime('now')),
(4, 2.8, 90, datetime('now', '-2 hours')),
(4, 3.0, 89, datetime('now', '-1 hours')),
(4, 2.9, 90, datetime('now'));

-- Sample alerts
INSERT INTO alerts (storage_unit_id, alert_type, severity, message, temperature_reading, created_at) VALUES
(1, 'HIGH_TEMP', 'warning', 'Temperature exceeded safe limit', 5.5, datetime('now', '-4 hours')),
(1, 'HIGH_TEMP', 'warning', 'Temperature above threshold', 5.2, datetime('now', '-5 hours'));

-- Sample maintenance log
INSERT INTO maintenance_logs (storage_unit_id, maintenance_type, description, performed_by, next_maintenance_due) VALUES
(1, 'Compressor Check', 'Regular compressor inspection and cleaning', 'Rajesh Kumar', datetime('now', '+30 days')),
(2, 'Sensor Calibration', 'Temperature sensor recalibration', 'Amit Singh', datetime('now', '+60 days'));
