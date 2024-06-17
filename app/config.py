import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '20120598'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///mycoin.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mycoin.db'

class ProductionConfig(Config):
    DEBUG = False
