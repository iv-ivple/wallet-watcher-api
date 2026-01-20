import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///wallet_watcher.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Web3 Configuration
    WEB3_PROVIDER_URI = os.getenv('WEB3_PROVIDER_URI', 'https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY')
    
    # Rate Limiting
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_DEFAULT = "100 per hour"
    
    # Background Worker
    SCHEDULER_API_ENABLED = True
    MONITOR_INTERVAL_SECONDS = 60  # Check wallets every 60 seconds

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace('postgresql://', 'postgresql+psycopg://')  # Must be set in production

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory database for tests
    SQLALCHEMY_ECHO = False
    WTF_CSRF_ENABLED = False  # Disable CSRF protection in tests
    SCHEDULER_API_ENABLED = False  # Disable background scheduler in tests
    WEB3_PROVIDER_URI = 'http://localhost:8545'  # Mock provider for tests

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,  # Added testing configuration
    'default': DevelopmentConfig
}
