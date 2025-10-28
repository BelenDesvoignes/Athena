# Archivo para manejar distintos ambientes de prueba
# le dice  database.py a que bd conectarse
import os
from os import environ

from src.core.database import db as main_db



class Config:
    TESTING = False
    SECRET_KEY = "your_secret_key"
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True
    SESSION_FILE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'flask_sessions')


class ProductionConfig(Config):
    MINIO_SERVER = environ.get("MINIO_SERVER")
    MINIO_ACCESS_KEY = environ.get("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = environ.get("MINIO_SECRET_KEY")
    MINIO_SECURE = True
    MINIO_BUCKET = "grupo19"
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")


class DevelopmentConfig(Config):
    MINIO_SERVER = "localhost:9000"
    MINIO_ACCESS_KEY = "grupo19admin"
    MINIO_SECRET_KEY = "grupo19secret"
    MINIO_SECURE = False    
    MINIO_BUCKET = "grupo19"
    SECRET_KEY = "your_dev_secret_key"
    DB_USER = "postgres"
    DB_PASSWORD = "admin"
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
