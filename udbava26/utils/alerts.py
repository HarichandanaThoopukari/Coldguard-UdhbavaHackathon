"""
Alert logic for Cold Storage Monitoring System
"""
from models.database import get_storage_unit, create_alert, get_active_alerts
from datetime import datetime, timedelta

class AlertManager:
    """Manages temperature alerts and notifications"""
    
    # Alert types
    ALERT_HIGH_TEMP = 'HIGH_TEMP'
    ALERT_LOW_TEMP = 'LOW_TEMP'
    ALERT_CRITICAL_HIGH = 'CRITICAL_HIGH'
    ALERT_CRITICAL_LOW = 'CRITICAL_LOW'
    ALERT_RAPID_CHANGE = 'RAPID_CHANGE'
    ALERT_POWER_FAILURE = 'POWER_FAILURE'
    ALERT_SENSOR_ERROR = 'SENSOR_ERROR'
    
    # Severity levels
    SEVERITY_INFO = 'info'
    SEVERITY_WARNING = 'warning'
    SEVERITY_CRITICAL = 'critical'
    
    # Thresholds
    RAPID_CHANGE_THRESHOLD = 3.0  # degrees per hour
    CRITICAL_MARGIN = 5.0  # degrees beyond safe range
    
    @classmethod
    def check_temperature(cls, unit_id, temperature, previous_readings=None):
        """
        Check temperature and generate alerts if needed
        
        Args:
            unit_id: Storage unit ID
            temperature: Current temperature reading
            previous_readings: List of recent readings for trend analysis
            
        Returns:
            List of generated alerts
        """
        alerts = []
        unit = get_storage_unit(unit_id)
        
        if not unit:
            return alerts
        
        min_safe = unit['min_temp']
        max_safe = unit['max_temp']
        unit_name = unit['name']
        
        # Check critical high temperature
        if temperature > max_safe + cls.CRITICAL_MARGIN:
            alert = cls._create_alert(
                unit_id=unit_id,
                alert_type=cls.ALERT_CRITICAL_HIGH,
                severity=cls.SEVERITY_CRITICAL,
                message=f"CRITICAL: Temperature at {temperature}°C in {unit_name}. "
                        f"Exceeds safe maximum ({max_safe}°C) by {temperature - max_safe:.1f}°C. "
                        f"Immediate action required!",
                temperature=temperature
            )
            alerts.append(alert)
            
        # Check high temperature warning
        elif temperature > max_safe:
            alert = cls._create_alert(
                unit_id=unit_id,
                alert_type=cls.ALERT_HIGH_TEMP,
                severity=cls.SEVERITY_WARNING,
                message=f"Warning: Temperature at {temperature}°C in {unit_name}. "
                        f"Above safe maximum of {max_safe}°C.",
                temperature=temperature
            )
            alerts.append(alert)
        
        # Check critical low temperature
        if temperature < min_safe - cls.CRITICAL_MARGIN:
            alert = cls._create_alert(
                unit_id=unit_id,
                alert_type=cls.ALERT_CRITICAL_LOW,
                severity=cls.SEVERITY_CRITICAL,
                message=f"CRITICAL: Temperature at {temperature}°C in {unit_name}. "
                        f"Below safe minimum ({min_safe}°C) by {min_safe - temperature:.1f}°C. "
                        f"Freezing damage possible!",
                temperature=temperature
            )
            alerts.append(alert)
            
        # Check low temperature warning
        elif temperature < min_safe:
            alert = cls._create_alert(
                unit_id=unit_id,
                alert_type=cls.ALERT_LOW_TEMP,
                severity=cls.SEVERITY_WARNING,
                message=f"Warning: Temperature at {temperature}°C in {unit_name}. "
                        f"Below safe minimum of {min_safe}°C.",
                temperature=temperature
            )
            alerts.append(alert)
        
        # Check for rapid temperature change
        if previous_readings and len(previous_readings) >= 2:
            rapid_change_alert = cls._check_rapid_change(
                unit_id, unit_name, temperature, previous_readings
            )
            if rapid_change_alert:
                alerts.append(rapid_change_alert)
        
        return alerts
    
    @classmethod
    def _check_rapid_change(cls, unit_id, unit_name, current_temp, previous_readings):
        """Check for rapid temperature changes"""
        # Get reading from ~1 hour ago if available
        one_hour_ago = datetime.now() - timedelta(hours=1)
        
        for reading in reversed(previous_readings):
            recorded_at = datetime.fromisoformat(reading['recorded_at'].replace('Z', '+00:00'))
            if recorded_at <= one_hour_ago:
                temp_diff = abs(current_temp - reading['temperature'])
                if temp_diff >= cls.RAPID_CHANGE_THRESHOLD:
                    direction = "risen" if current_temp > reading['temperature'] else "dropped"
                    return cls._create_alert(
                        unit_id=unit_id,
                        alert_type=cls.ALERT_RAPID_CHANGE,
                        severity=cls.SEVERITY_WARNING,
                        message=f"Rapid temperature change detected in {unit_name}. "
                                f"Temperature has {direction} by {temp_diff:.1f}°C in the last hour. "
                                f"Check for equipment issues or door left open.",
                        temperature=current_temp
                    )
                break
        
        return None
    
    @classmethod
    def _create_alert(cls, unit_id, alert_type, severity, message, temperature):
        """Create and store alert"""
        alert_id = create_alert(unit_id, alert_type, severity, message, temperature)
        return {
            'id': alert_id,
            'unit_id': unit_id,
            'type': alert_type,
            'severity': severity,
            'message': message,
            'temperature': temperature,
            'created_at': datetime.now().isoformat()
        }
    
    @classmethod
    def create_power_failure_alert(cls, unit_id, unit_name):
        """Create alert for power failure"""
        return cls._create_alert(
            unit_id=unit_id,
            alert_type=cls.ALERT_POWER_FAILURE,
            severity=cls.SEVERITY_CRITICAL,
            message=f"POWER FAILURE detected in {unit_name}. "
                    f"Cooling system may be affected. Check backup power.",
            temperature=None
        )
    
    @classmethod
    def get_alert_summary(cls):
        """Get summary of active alerts by severity"""
        alerts = get_active_alerts()
        summary = {
            'critical': 0,
            'warning': 0,
            'info': 0,
            'total': len(alerts)
        }
        
        for alert in alerts:
            severity = alert.get('severity', 'info')
            if severity in summary:
                summary[severity] += 1
        
        return summary
    
    @classmethod
    def format_alert_for_sms(cls, alert):
        """Format alert message for SMS notification"""
        severity_emoji = {
            'critical': '🚨',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
        emoji = severity_emoji.get(alert.get('severity', 'info'), '')
        
        return f"{emoji} Cold Storage Alert\n{alert['message'][:140]}"
    
    @classmethod
    def should_notify(cls, alert, last_notification_time=None, cooldown_minutes=15):
        """
        Determine if notification should be sent
        Prevents alert flooding by enforcing cooldown
        """
        if alert.get('severity') == cls.SEVERITY_CRITICAL:
            # Always notify for critical alerts
            return True
        
        if last_notification_time is None:
            return True
        
        time_diff = datetime.now() - last_notification_time
        return time_diff.total_seconds() >= cooldown_minutes * 60


def evaluate_temperature(unit_id, temperature, previous_readings=None):
    """
    Convenience function to evaluate temperature
    Returns status and any generated alerts
    """
    unit = get_storage_unit(unit_id)
    if not unit:
        return {'status': 'error', 'message': 'Unit not found'}
    
    alerts = AlertManager.check_temperature(unit_id, temperature, previous_readings)
    
    min_safe = unit['min_temp']
    max_safe = unit['max_temp']
    
    if temperature < min_safe or temperature > max_safe:
        status = 'critical' if alerts and any(a['severity'] == 'critical' for a in alerts) else 'warning'
    else:
        status = 'normal'
    
    return {
        'status': status,
        'temperature': temperature,
        'min_safe': min_safe,
        'max_safe': max_safe,
        'in_range': min_safe <= temperature <= max_safe,
        'alerts': alerts
    }
