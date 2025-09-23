from flask import Flask
from src.web.controllers.admin_routes import admin_bp
from src.web.config import config
from src.core.database import db

def create_app(env='development'):
    app = Flask(__name__, static_folder='src/web/static')
    
    #cargar la configuracion
    app.config.from_object(config[env])
    
    #inicializar la bd
    db.init_app(app)
    
    #registrar el blueprint
    app.register_blueprint(admin_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)