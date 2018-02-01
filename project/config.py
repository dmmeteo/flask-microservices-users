class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False


class DevelopmentConfig(BaseConfig):
    """Base configuration"""
    DEBUG = True


class TestingConfig(BaseConfig):
    """Base configuration"""
    DEBUG = True
    TESTING = True


class ProductionConfig(BaseConfig):
    """Base configuration"""
    DEBUG = False
