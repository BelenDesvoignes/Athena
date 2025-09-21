from flask import Flask 
from src.web.controllers.admin_routes import admin_bp

def create_app():
    # Modifica esta línea para indicar la carpeta 'static'
    app = Flask(__name__, static_folder='src/web/static')
    app.register_blueprint(admin_bp)    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)