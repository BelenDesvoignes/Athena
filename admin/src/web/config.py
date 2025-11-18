import os
from os import environ

from src.core.database import db as main_db


class Config:
    TESTING = False
    SECRET_KEY = "your_secret_key"
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True
    SESSION_FILE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'flask_sessions')

    # 🚨 AJUSTE PRINCIPAL: Definimos JWT_SECRET_KEY en la base
    # Usamos la variable de entorno, pero damos un fallback seguro si falla.
    # El valor final será sobreescrito por ProductionConfig o DevelopmentConfig.
    # Esto es solo una precaución.
    JWT_SECRET_KEY = environ.get("JWT_SECRET_KEY", "DEFAULT_SUPER_SECRET_FALLBACK")


class ProductionConfig(Config):
    MINIO_SERVER = environ.get("MINIO_SERVER")
    MINIO_ACCESS_KEY = environ.get("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = environ.get("MINIO_SECRET_KEY")
    MINIO_SECURE = True
    MINIO_BUCKET = "grupo19"
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")
    JWT_SECRET_KEY = environ.get("JWT_SECRET_KEY")

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
    JWT_SECRET_KEY = "grupo19"


class TestingConfig(Config):
    TESTING = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}