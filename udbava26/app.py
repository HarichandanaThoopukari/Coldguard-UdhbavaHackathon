"""
Cold Storage Temperature Monitoring System
Main Flask Application
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import os

from models.database import (
    init_db, get_all_storage_units, get_storage_unit,
    add_temperature_reading, get_temperature_history,
    get_active_alerts, get_all_alerts, acknowledge_alert,
    log_power_failure, get_power_failures,
    add_maintenance_log, get_maintenance_logs,
    generate_daily_report, get_daily_reports,
    get_analytics_data, get_dashboard_summary,
    get_all_recent_readings
)
from utils.alerts import AlertManager, evaluate_temperature
from config import config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config['default'])

# Initialize database on startup
if not os.path.exists('cold_storage.db'):
    init_db()

# ==================== WEB ROUTES ====================

@app.route('/')
def index():
    """Dashboard home page"""
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard view"""
    units = get_all_storage_units()
    summary = get_dashboard_summary()
    active_alerts = get_active_alerts()[:5]  # Latest 5 alerts
    return render_template('dashboard.html', 
                         units=units, 
                         summary=summary,
                         alerts=active_alerts)

@app.route('/alerts')
def alerts_page():
    """Alerts management page"""
    alerts = get_all_alerts(limit=100)
    summary = AlertManager.get_alert_summary()
    return render_template('alerts.html', alerts=alerts, summary=summary)

@app.route('/reports')
def reports_page():
    """Reports page"""
    units = get_all_storage_units()
    reports = get_daily_reports(days=30)
    return render_template('reports.html', units=units, reports=reports)

@app.route('/maintenance')
def maintenance_page():
    """Maintenance logs page"""
    units = get_all_storage_units()
    logs = get_maintenance_logs(limit=50)
    return render_template('maintenance.html', units=units, logs=logs)

@app.route('/settings')
def settings_page():
    """Settings page"""
    units = get_all_storage_units()
    return render_template('settings.html', units=units)

# ==================== API ROUTES ====================

@app.route('/api/units', methods=['GET'])
def api_get_units():
    """Get all storage units"""
    units = get_all_storage_units()
    return jsonify({'success': True, 'data': units})

@app.route('/api/units/<int:unit_id>', methods=['GET'])
def api_get_unit(unit_id):
    """Get single storage unit"""
    unit = get_storage_unit(unit_id)
    if unit:
        return jsonify({'success': True, 'data': unit})
    return jsonify({'success': False, 'error': 'Unit not found'}), 404

@app.route('/api/temperature', methods=['POST'])
def api_add_temperature():
    """Add new temperature reading"""
    data = request.json
    
    if not data or 'unit_id' not in data or 'temperature' not in data:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    unit_id = data['unit_id']
    temperature = float(data['temperature'])
    humidity = data.get('humidity')
    recorded_by = data.get('recorded_by', 'System')
    is_manual = data.get('is_manual', False)
    
    # Add reading
    reading_id = add_temperature_reading(unit_id, temperature, humidity, recorded_by, is_manual)
    
    # Get previous readings for trend analysis
    previous = get_temperature_history(unit_id, hours=2)
    
    # Evaluate temperature and generate alerts
    evaluation = evaluate_temperature(unit_id, temperature, previous)
    
    return jsonify({
        'success': True,
        'reading_id': reading_id,
        'evaluation': evaluation
    })

@app.route('/api/temperature/<int:unit_id>/history', methods=['GET'])
def api_temperature_history(unit_id):
    """Get temperature history for a unit"""
    hours = request.args.get('hours', 24, type=int)
    history = get_temperature_history(unit_id, hours)
    return jsonify({'success': True, 'data': history})

@app.route('/api/alerts', methods=['GET'])
def api_get_alerts():
    """Get alerts"""
    active_only = request.args.get('active', 'false').lower() == 'true'
    if active_only:
        alerts = get_active_alerts()
    else:
        alerts = get_all_alerts(limit=100)
    return jsonify({'success': True, 'data': alerts})

@app.route('/api/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def api_acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    data = request.json or {}
    acknowledged_by = data.get('acknowledged_by', 'System')
    acknowledge_alert(alert_id, acknowledged_by)
    return jsonify({'success': True})

@app.route('/api/power-failure', methods=['POST'])
def api_log_power_failure():
    """Log power failure"""
    data = request.json
    
    if not data or 'unit_id' not in data:
        return jsonify({'success': False, 'error': 'Missing unit_id'}), 400
    
    unit_id = data['unit_id']
    start_time = datetime.fromisoformat(data.get('start_time', datetime.now().isoformat()))
    end_time = data.get('end_time')
    if end_time:
        end_time = datetime.fromisoformat(end_time)
    
    failure_id = log_power_failure(
        unit_id=unit_id,
        start_time=start_time,
        end_time=end_time,
        cause=data.get('cause'),
        notes=data.get('notes'),
        reported_by=data.get('reported_by', 'System')
    )
    
    # Generate alert
    unit = get_storage_unit(unit_id)
    if unit:
        AlertManager.create_power_failure_alert(unit_id, unit['name'])
    
    return jsonify({'success': True, 'failure_id': failure_id})

@app.route('/api/power-failures', methods=['GET'])
def api_get_power_failures():
    """Get power failure history"""
    unit_id = request.args.get('unit_id', type=int)
    days = request.args.get('days', 30, type=int)
    failures = get_power_failures(unit_id, days)
    return jsonify({'success': True, 'data': failures})

@app.route('/api/maintenance', methods=['POST'])
def api_add_maintenance():
    """Add maintenance log"""
    data = request.json
    
    required = ['unit_id', 'maintenance_type', 'performed_by']
    if not all(k in data for k in required):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    log_id = add_maintenance_log(
        unit_id=data['unit_id'],
        maintenance_type=data['maintenance_type'],
        description=data.get('description', ''),
        performed_by=data['performed_by'],
        next_due=data.get('next_maintenance_due'),
        cost=data.get('cost'),
        status=data.get('status', 'Completed')
    )
    
    return jsonify({'success': True, 'log_id': log_id})

@app.route('/api/maintenance', methods=['GET'])
def api_get_maintenance():
    """Get maintenance logs"""
    unit_id = request.args.get('unit_id', type=int)
    logs = get_maintenance_logs(unit_id)
    return jsonify({'success': True, 'data': logs})

@app.route('/api/reports/generate', methods=['POST'])
def api_generate_report():
    """Generate daily report"""
    data = request.json or {}
    unit_id = data.get('unit_id')
    report_date = data.get('date')
    
    if report_date:
        report_date = datetime.fromisoformat(report_date).date()
    
    if unit_id:
        report = generate_daily_report(unit_id, report_date)
        return jsonify({'success': True, 'report': report})
    else:
        # Generate for all units
        units = get_all_storage_units()
        reports = []
        for unit in units:
            report = generate_daily_report(unit['id'], report_date)
            reports.append(report)
        return jsonify({'success': True, 'reports': reports})

@app.route('/api/reports', methods=['GET'])
def api_get_reports():
    """Get daily reports"""
    unit_id = request.args.get('unit_id', type=int)
    days = request.args.get('days', 7, type=int)
    reports = get_daily_reports(unit_id, days)
    return jsonify({'success': True, 'data': reports})

@app.route('/api/analytics/<int:unit_id>', methods=['GET'])
def api_get_analytics(unit_id):
    """Get analytics data"""
    days = request.args.get('days', 7, type=int)
    analytics = get_analytics_data(unit_id, days)
    return jsonify({'success': True, 'data': analytics})

@app.route('/api/dashboard/summary', methods=['GET'])
def api_dashboard_summary():
    """Get dashboard summary"""
    summary = get_dashboard_summary()
    return jsonify({'success': True, 'data': summary})

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Not found'}), 404
    return render_template('base.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Server error'}), 500
    return render_template('base.html', error='Server error'), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    print("=" * 60)
    print("  Cold Storage Temperature Monitoring System")
    print("  Starting server at [127.0.0.1](http://127.0.0.1:5000)")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
