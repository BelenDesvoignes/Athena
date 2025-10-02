from flask import Flask, jsonify, render_template, abort, session, g
from src.core import database
from src.web.config import config
from flask_session import Session
from src.web.handlers.auth import login_required
from src.web.controllers.auth import auth_bp
from src.web.controllers.user_routes import user_admin_bp

app = Flask(__name__)


def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)

    app.config.from_object(config[env])
    # carga la configuracion segun el entorno

    #inicializar la session
    Session(app) 
    # inicializa la bd
    database.init_db(app)

    
    
    
    #registro de blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_admin_bp, url_prefix="/admin/users")


    #manejo de errores
    @app.route("/not_found")
    @app.errorhandler(404)
    def not_found(error):
        return render_template("error_404.html"), 404


    @app.route("/internal_error")
    def error_500():
        return abort(500)

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("error_500.html"), 500


    @app.route("/protected")
    def error_401():
        return abort(401)

    @app.errorhandler(401)
    def unauthorized(error):
        return render_template("error_401.html"), 401

    
    return app
