from flask import Flask, render_template, session
from flask_session import Session

from src.core.database import db, reset_db
from src.core.flags import is_flag_enabled
from src.core.models.feature_flags import FeatureFlag
from src.core.permissions_service import current_user_permissions
from src.core.seeds import seed_admin_user, seed_feature_flags, seed_roles_permissions, seed_sitios

from src.web.config import config
from src.web.storage import storage
from src.web.controllers.auth import auth_bp
from src.web.controllers.sites_routes import bp_sitios
from src.web.controllers.tag_routes import tag_bp
from src.web.controllers.user_routes import user_admin_bp
from src.web.handlers.maintenance import maintenance_check
from src.web.controllers.review_routes import reviews_bp

from src.web.controllers.feature_flags_routes import feature_flags_bp
from src.web.api.api import api_bp
from src.web.controllers.public_user_routes import public_users_bp



from flask_cors import CORS


def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder,template_folder="templates")

    app.config.from_object(config[env])
    # carga la configuracion segun el entorno

    allowed_origins = ["https://grupo19.proyecto2025.linti.unlp.edu.ar"]
    if env == "development":
        # Nota: Usamos http y el puerto de tu frontend (5173)
        allowed_origins.append("http://localhost:5173")
        allowed_origins.append("http://127.0.0.1:5173") 

    #inicializar la session
    Session(app) 
    CORS(app, origins=allowed_origins)


    db.init_app(app)
    
    try:
        minio_server = app.config.get("MINIO_SERVER")
        access_key = app.config.get("MINIO_ACCESS_KEY")
        secret_key = app.config.get("MINIO_SECRET_KEY")
        secure = app.config.get("MINIO_SECURE")

        app.logger.info(f"🔧 Configuración MinIO detectada:")
        app.logger.info(f"    ➜ Server: {minio_server}")
        app.logger.info(f"    ➜ Secure: {secure}")
        app.logger.info(f"    ➜ Access Key: {access_key}" if access_key else "    ➜ Access Key: NO DEFINIDA")
        app.logger.info(f"    ➜ Secret Key: {secret_key}" if secret_key else "    ➜ Secret Key: NO DEFINIDA")
    except Exception as e:
        app.logger.warning(f"⚠️ No se pudieron registrar las credenciales de MinIO: {str(e)}")

    # Inicializar cliente de MinIO (maneja errores internamente)
    
    try:
        storage.init_app(app)
    except Exception as e:
        app.logger.error(f"❌ Fallo al inicializar MinIO: {str(e)}")
    
    
    with app.app_context():
        from src.core.models.user import User
        from src.core.models.site import Sitio
        from src.core.models.review import Review
        from src.core.models.feature_flags import FeatureFlag
        from src.core.models.public_user import PublicUser
        from src.core.models.favorites import Favorite
        db.create_all()
        seed_roles_permissions() 
        seed_admin_user()        
        seed_feature_flags()
        seed_sitios()
        
    # inicializa la bd
    app.jinja_env.globals['current_user_permissions'] = current_user_permissions
    app.jinja_env.globals['is_flag_enabled'] = is_flag_enabled

    #registro de blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    #app.register_blueprint(user_admin_bp, url_prefix="/admin/users")
    app.register_blueprint(tag_bp, url_prefix="/tags")
    app.register_blueprint(user_admin_bp, url_prefix="/admin")
    app.register_blueprint(feature_flags_bp)
    app.register_blueprint(bp_sitios, url_prefix="/sitios")
    app.register_blueprint(reviews_bp, url_prefix="/reviews")
    app.register_blueprint(api_bp)
    app.register_blueprint(public_users_bp)


    #rutas principales 
    @app.route("/")
    def index():
        return render_template("index.html")
    
    @app.route("/limpiar_sesion")
    def limpiar_sesion():
        session.clear()
        return "Sesión borrada"
    
    @app.cli.command("reset-db")
    def reset_db_command():
        reset_db() #elimina y recrea la estructura de la bd 
        with app.app_context(): 
            seed_roles_permissions() #insertar roles
            seed_admin_user()        #crear el admin
            print("Base de datos reseteada e inicializada con roles y admin.")

    @app.context_processor
    def inject_flags():
        # Cargar flags de la BD
        flags = db.session.query(FeatureFlag).all()
        feature_flags = {f.key: f.is_enabled for f in flags}

        return {
            "feature_flags": feature_flags
        }
        
    maintenance_check(app)

    #manejo de errores
    @app.route("/not_found")
    @app.errorhandler(404)
    def not_found(error):
        return render_template("error_404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("error_500.html"), 500

    @app.errorhandler(401)
    def unauthorized(error):
        return render_template("error_401.html"), 401

    
    return app
