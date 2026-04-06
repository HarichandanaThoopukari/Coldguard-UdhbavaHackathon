"""
Configuration settings for Cold Storage Monitoring System
"""
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cold-storage-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///cold_storage.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Temperature thresholds (in Celsius)
    TEMP_MIN_SAFE = -5.0
    TEMP_MAX_SAFE = 8.0
    TEMP_CRITICAL_HIGH = 12.0
    TEMP_CRITICAL_LOW = -10.0
    
    # Alert settings
    ALERT_CHECK_INTERVAL = 60  # seconds
    DATA_RETENTION_DAYS = 365
    
    # Supported storage types
    STORAGE_TYPES = ['Potato', 'Vegetable', 'Fruit', 'Mixed']

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
