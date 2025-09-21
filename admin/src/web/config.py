# archivo para manejar distintos ambientes de prueba 

from flask import Flask
from flask import render_template
from src.web.controllers import db as main_db
from os import environ


class Config:
    TESTING = False
    SECRET_KEY ="your_secret_key"
    SESSION_TYPE = "filesystem"

class ProductionConfig(Config):
    SQLALCHEMY_ENGINE = {"default": environ.get("DATABASE_URL")}


class DevelopmentConfig(Config):
    SECRET_KEY = "your_dev_secret_key"
    DB_USER = "postgres"
    DB_PASSWORD = "admin"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "grupo19"
    DB_SCHEME = "postgresql+psycopg2"

    SQLALCHEMY_ENGINE = {
        "default": f"{DB_SCHEME}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    }

class TestingConfig(Config):
    TESTING = True
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
} 