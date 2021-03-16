import os

class Config(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SECRET_KEY = 'secret'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    JWT_COOKIE_SECURE = False
    JWT_TOKEN_LOCATION = ["cookies"]

class ProductionConfig(Config):
    pass

class DevelopConfig(Config):
    pass