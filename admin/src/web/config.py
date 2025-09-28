# archivo para manejar distintos ambientes de prueba
# le dice  database.py a que bd conectarse


from flask import Flask
from flask import render_template
from src.core.database import db as main_db
from os import environ


class Config:
    TESTING = False
    SECRET_KEY = "your_secret_key"
    SESSION_TYPE = "filesystem"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")


class DevelopmentConfig(Config):
    SECRET_KEY = "your_development_secret_key"
    DB_USER =  environ.get("DB_USER") or "postgres"
    DB_PASSWORD = environ.get("DB_PASSWORD") or "postgres"
    DB_HOST = environ.get("DB_HOST") or "localhost"
    DB_PORT = environ.get("DB_PORT") or "5432"
    DB_NAME = environ.get("DB_NAME") or "grupo19"
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
