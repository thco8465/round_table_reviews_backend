import os

class Config:
    """Base configuration."""
    USERNAME = os.getenv('DB_USERNAME', 'root')
    PASSWORD = os.getenv('DB_PASSWORD', None)
    DATABASE = os.getenv('DB_DATABASE', 'database_production')
    HOST = os.getenv('DB_HOST', '127.0.0.1')
    DIALECT = 'postgres'

class DevelopmentConfig(Config):
    """Development configuration."""
    USERNAME = 'postgres'
    PASSWORD = 'ArkhamknightN7?'
    DATABASE = 'gamespective'

class TestingConfig(Config):
    """Testing configuration."""
    USERNAME = 'root'
    PASSWORD = None
    DATABASE = 'database_test'

class ProductionConfig(Config):
    """Production configuration."""
    USERNAME = 'root'
    PASSWORD = None
    DATABASE = 'database_production'

# Set the configuration based on the environment variable
def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'development':
        return DevelopmentConfig
    elif env == 'testing':
        return TestingConfig
    elif env == 'production':
        return ProductionConfig
    else:
        raise ValueError("Invalid environment name.")

# Usage example:
# from config import get_config
# app.config.from_object(get_config())
