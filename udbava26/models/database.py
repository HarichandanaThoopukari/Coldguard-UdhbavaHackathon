"""
Database operations for Cold Storage Monitoring System
"""
import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager
import os

DATABASE_PATH = 'cold_storage.db'

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database with schema"""
    if os.path.exists('database.sql'):
        with open('database.sql', 'r') as f:
            schema = f.read()
        with get_db_connection() as conn:
            conn.executescript(schema)
            conn.commit()
        print("Database initialized successfully!")
    else:
        print("Warning: database.sql not found")

def get_all_storage_units():
    """Get all active storage units"""
    with get_db_connection() as conn:
        cursor = conn.execute('''
            SELECT su.*, 
                   (SELECT temperature FROM temperature_readings 
                    WHERE storage_unit_id = su.id 
                    ORDER BY recorded_at DESC LIMIT 1) as current_temp,
                   (SELECT humidity FROM temperature_readings 
                    WHERE storage_unit_id = su.id 
                    ORDER BY recorded_at DESC LIMIT 1) as current_humidity,
                   (SELECT COUNT(*) FROM alerts 
                    WHERE storage_unit_id = su.id 
                    AND is_acknowledged = 0) as active_alerts
            FROM storage_units su
            WHERE su.is_active = 1
            ORDER BY su.name
        ''')
        return [dict(row) for row in cursor.fetchall()]

def get_storage_unit(unit_id):
    """Get single storage unit details"""
    with get_db_connection() as conn:
        cursor = conn.execute('''
            SELECT * FROM storage_units WHERE id = ?
        ''', (unit_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def add_temperature_reading(unit_id, temperature, humidity=None, recorded_by=None, is_manual=False):
    """Add new temperature reading"""
    with get_db_connection() as conn:
        cursor = conn.execute('''
            INSERT INTO temperature_readings 
            (storage_unit_id, temperature, humidity, recorded_by, is_manual)
            VALUES (?, ?, ?, ?, ?)
        ''', (unit_id, temperature, humidity, recorded_by, is_manual))
        conn.commit()
        return cursor.lastrowid

def get_temperature_history(unit_id, hours=24):
    """Get temperature readings for specified hours"""
    with get_db_connection() as conn:
        cursor = conn.execute('''
            SELECT id, temperature, humidity, recorded_at
            FROM temperature_readings
            WHERE storage_unit_id = ?
            AND recorded_at >= datetime('now', ?)
            ORDER BY recorded_at ASC
        ''', (unit_id, f'-{hours} hours'))
        return [dict(row) for row in cursor.fetchall()]

def get_all_recent_readings(hours=24):
    """Get recent readings for all units"""
    with get_db_connection() as conn:
        cursor = conn.execute('''
            SELECT tr.*, su.name as unit_name
            FROM temperature_readings tr
            JOIN storage_units su ON tr.storage_unit_id = su.id
            WHERE tr.recorded_at >= datetime('now', ?)
            ORDER BY tr.recorded_at DESC
        ''', (f'-{hours} hours',))
        return [dict(row) for row in cursor.fetchall()]

def create_alert(unit_id, alert_type, severity, message, temperature=None):
    """Create new alert"""
    with get_db_connection() as conn:
        cursor = conn.execute('''
            INSERT INTO alerts 
            (storage_unit_id, alert_type, severity, message, temperature_reading)
            VALUES (?, ?, ?, ?, ?)
        ''', (unit_id, alert_type, severity, message, temperature))
        conn.commit()
        return cursor.lastrowid

def get_active_alerts():
    """Get all unacknowledged alerts"""
    with get_db_connection() as conn:
        cursor = conn.execute('''
            SELECT a.*, su.name as unit_name
            FROM alerts a
            JOIN storage_units su ON a.storage_unit_id = su.id
            WHERE a.is_acknowledged = 0
            ORDER BY a.created_at DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]

def get_all_alerts(limit=100):
    """Get all alerts"""
    with get_db_connection() as conn:
        cursor = conn.execute('''
            SELECT a.*, su.name as unit_name
            FROM alerts a
            JOIN storage_units su ON a.storage_unit_id = su.id
            ORDER BY a.created_at DESC
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]

def acknowledge_alert(alert_id, acknowledged_by):
    """Acknowledge an alert"""
    with get_db_connection() as conn:
        conn.execute('''
            UPDATE alerts 
            SET is_acknowledged = 1, 
                acknowledged_by = ?,
                acknowledged_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (acknowledged_by, alert_id))
        conn.commit()

def log_power_failure(unit_id, start_time, end_time=None, cause=None, notes=None, reported_by=None):
    """Log power failure event"""
    duration = None
    if end_time and start_time:
        duration = int((end_time - start_time).total_seconds() / 60)
    
    with get_db_connection() as conn:
        cursor = conn.execute('''
            INSERT INTO power_failures 
            (storage_unit_id, start_time, end_time, duration_minutes, cause, notes, reported_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (unit_id, start_time, end_time, duration, cause, notes, reported_by))
        conn.commit()
        return cursor.lastrowid

def get_power_failures(unit_id=None, days=30):
    """Get power failure history"""
    with get_db_connection() as conn:
        if unit_id:
            cursor = conn.execute('''
                SELECT pf.*, su.name as unit_name
                FROM power_failures pf
                JOIN storage_units su ON pf.storage_unit_id = su.id
                WHERE pf.storage_unit_id = ?
                AND pf.start_time >= datetime('now', ?)
                ORDER BY pf.start_time DESC
            ''', (unit_id, f'-{days} days'))
        else:
            cursor = conn.execute('''
                SELECT pf.*, su.name as unit_name
                FROM power_failures pf
                JOIN storage_units su ON pf.storage_unit_id = su.id
                WHERE pf.start_time >= datetime('now', ?)
                ORDER BY pf.start_time DESC
            ''', (f'-{days} days',))
        return [dict(row) for row in cursor.fetchall()]

def add_maintenance_log(unit_id, maintenance_type, description, performed_by, 
                        next_due=None, cost=None, status='Completed'):
    """Add maintenance log entry"""
    with get_db_connection() as conn:
        cursor = conn.execute('''
            INSERT INTO maintenance_logs 
            (storage_unit_id, maintenance_type, description, performed_by, 
             next_maintenance_due, cost, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (unit_id, maintenance_type, description, performed_by, next_due, cost, status))
        conn.commit()
        return cursor.lastrowid

def get_maintenance_logs(unit_id=None, limit=50):
    """Get maintenance logs"""
    with get_db_connection() as conn:
        if unit_id:
            cursor = conn.execute('''
                SELECT ml.*, su.name as unit_name
                FROM maintenance_logs ml
                JOIN storage_units su ON ml.storage_unit_id = su.id
                WHERE ml.storage_unit_id = ?
                ORDER BY ml.performed_at DESC
                LIMIT ?
            ''', (unit_id, limit))
        else:
            cursor = conn.execute('''
                SELECT ml.*, su.name as unit_name
                FROM maintenance_logs ml
                JOIN storage_units su ON ml.storage_unit_id = su.id
                ORDER BY ml.performed_at DESC
                LIMIT ?
            ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]

def generate_daily_report(unit_id, report_date=None):
    """Generate daily report for a storage unit"""
    if report_date is None:
        report_date = datetime.now().date()
    
    with get_db_connection() as conn:
        # Get temperature statistics
        cursor = conn.execute('''
            SELECT 
                MIN(temperature) as min_temp,
                MAX(temperature) as max_temp,
                AVG(temperature) as avg_temp,
                COUNT(*) as total_readings
            FROM temperature_readings
            WHERE storage_unit_id = ?
            AND DATE(recorded_at) = ?
        ''', (unit_id, report_date))
        stats = dict(cursor.fetchone())
        
        # Get alerts count
        cursor = conn.execute('''
            SELECT COUNT(*) as alerts_count
            FROM alerts
            WHERE storage_unit_id = ?
            AND DATE(created_at) = ?
        ''', (unit_id, report_date))
        alerts = dict(cursor.fetchone())
        
        # Get power failures count
        cursor = conn.execute('''
            SELECT COUNT(*) as power_failures_count
            FROM power_failures
            WHERE storage_unit_id = ?
            AND DATE(start_time) = ?
        ''', (unit_id, report_date))
        power = dict(cursor.fetchone())
        
        # Determine status
        status = 'Normal'
        if alerts['alerts_count'] > 0:
            status = 'Alerts Recorded'
        if power['power_failures_count'] > 0:
            status = 'Power Issues'
        
        # Insert or update report
        cursor = conn.execute('''
            INSERT OR REPLACE INTO daily_reports 
            (storage_unit_id, report_date, min_temp, max_temp, avg_temp, 
             total_readings, alerts_count, power_failures_count, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (unit_id, report_date, stats['min_temp'], stats['max_temp'], 
              stats['avg_temp'], stats['total_readings'], 
              alerts['alerts_count'], power['power_failures_count'], status))
        conn.commit()
        
        return {
            'unit_id': unit_id,
            'report_date': str(report_date),
            **stats,
            **alerts,
            **power,
            'status': status
        }

def get_daily_reports(unit_id=None, days=7):
    """Get daily reports"""
    with get_db_connection() as conn:
        if unit_id:
            cursor = conn.execute('''
                SELECT dr.*, su.name as unit_name
                FROM daily_reports dr
                JOIN storage_units su ON dr.storage_unit_id = su.id
                WHERE dr.storage_unit_id = ?
                AND dr.report_date >= DATE('now', ?)
                ORDER BY dr.report_date DESC
            ''', (unit_id, f'-{days} days'))
        else:
            cursor = conn.execute('''
                SELECT dr.*, su.name as unit_name
                FROM daily_reports dr
                JOIN storage_units su ON dr.storage_unit_id = su.id
                WHERE dr.report_date >= DATE('now', ?)
                ORDER BY dr.report_date DESC
            ''', (f'-{days} days',))
        return [dict(row) for row in cursor.fetchall()]

def get_analytics_data(unit_id, days=7):
    """Get analytics data for a unit"""
    with get_db_connection() as conn:
        # Daily averages
        cursor = conn.execute('''
            SELECT 
                DATE(recorded_at) as date,
                MIN(temperature) as min_temp,
                MAX(temperature) as max_temp,
                AVG(temperature) as avg_temp,
                AVG(humidity) as avg_humidity,
                COUNT(*) as reading_count
            FROM temperature_readings
            WHERE storage_unit_id = ?
            AND recorded_at >= datetime('now', ?)
            GROUP BY DATE(recorded_at)
            ORDER BY date ASC
        ''', (unit_id, f'-{days} days'))
        daily_stats = [dict(row) for row in cursor.fetchall()]
        
        # Alert distribution
        cursor = conn.execute('''
            SELECT 
                alert_type,
                severity,
                COUNT(*) as count
            FROM alerts
            WHERE storage_unit_id = ?
            AND created_at >= datetime('now', ?)
            GROUP BY alert_type, severity
        ''', (unit_id, f'-{days} days'))
        alert_distribution = [dict(row) for row in cursor.fetchall()]
        
        return {
            'daily_stats': daily_stats,
            'alert_distribution': alert_distribution
        }

def get_dashboard_summary():
    """Get summary data for dashboard"""
    with get_db_connection() as conn:
        # Total units
        cursor = conn.execute('SELECT COUNT(*) as count FROM storage_units WHERE is_active = 1')
        total_units = cursor.fetchone()['count']
        
        # Active alerts
        cursor = conn.execute('SELECT COUNT(*) as count FROM alerts WHERE is_acknowledged = 0')
        active_alerts = cursor.fetchone()['count']
        
        # Today's readings
        cursor = conn.execute('''
            SELECT COUNT(*) as count FROM temperature_readings 
            WHERE DATE(recorded_at) = DATE('now')
        ''')
        today_readings = cursor.fetchone()['count']
        
        # Units with issues (temp outside range)
        cursor = conn.execute('''
            SELECT COUNT(DISTINCT tr.storage_unit_id) as count
            FROM temperature_readings tr
            JOIN storage_units su ON tr.storage_unit_id = su.id
            WHERE tr.id IN (
                SELECT MAX(id) FROM temperature_readings 
                GROUP BY storage_unit_id
            )
            AND (tr.temperature < su.min_temp OR tr.temperature > su.max_temp)
        ''')
        units_with_issues = cursor.fetchone()['count']
        
        return {
            'total_units': total_units,
            'active_alerts': active_alerts,
            'today_readings': today_readings,
            'units_with_issues': units_with_issues
        }
