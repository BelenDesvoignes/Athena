# archivo para manejar distintos ambientes de prueba
# le dice  database.py a que bd conectarse
from flask import Flask
from flask import render_template
from src.core.database import db as main_db
from os import environ
import os 


class Config:
    TESTING = False
    SECRET_KEY = "your_secret_key"
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True
    SESSION_FILE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'flask_sessions')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")


class DevelopmentConfig(Config):
    SECRET_KEY = "your_dev_secret_key"
    DB_USER = "postgres"
    DB_PASSWORD = "Qwerty01"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "grupo19"
    DB_SCHEME = "postgresql+psycopg2"

    SQLALCHEMY_DATABASE_URI = (
        f"{DB_SCHEME}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )


class TestingConfig(Config):
    TESTING = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
