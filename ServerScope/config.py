import os

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Configuration for development."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///dev_serverscope.db'
    FLASK_ENV = 'development'

class TestingConfig(Config):
    """Configuration for testing."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///test_serverscope.db'
    WTF_CSRF_ENABLED = False  # Often turned off for testing forms
    FLASK_ENV = 'testing'

class ProductionConfig(Config):
    """Configuration for production."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///prod_serverscope.db'
    FLASK_ENV = 'production'

class StagingConfig(Config):
    """Configuration for staging."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('STAGING_DATABASE_URL') or 'sqlite:///staging_serverscope.db'
    FLASK_ENV = 'staging'

