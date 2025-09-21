# archivo para manejar distintos ambientes de prueba 

from flask import Flask
from flask import render_template
from src.web.controllers import db as main_db




class Config:
    TESTING = False
    SECRET_KEY ="your_secret_key"
    SESSION_TYPE = "filesystem"

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    pass

class TestingConfig(Config):
    TESTING = True
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
} 

    


