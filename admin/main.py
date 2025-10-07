from flask import Flask, render_template, g, session
from src.web.config import config
from src.core.database import db, reset_db
from src.core.permissions_service import current_user_permissions
from src.core.flags import is_flag_enabled
from src.web.controllers.auth import auth_bp
from src.web.controllers.user_routes import user_admin_bp
from src.web.controllers.feature_flags import feature_flags_bp
from src.core.seeds import seed_roles_permissions, seed_admin_user, seed_feature_flags
from src.web.controllers.tag_routes import tag_bp
from src.web.handlers.maintenance import maintenance_check
from src.core.models.feature_flags import FeatureFlag
from src.web.config import config
from src.core.models.role_permission import Role, Permission, RolePermission 
from src.core.models.user import User 

def create_app(env="development"):
    # configura la carpeta de archivos estáticos y la de plantillas.
    app = Flask(
        __name__, static_folder="src/web/static", template_folder="src/web/templates"
    )
    # carga la configuración del ambiente.
    app.config.from_object(config[env])

    # inicializa la base de datos con la aplicación.
    db.init_app(app)
    app.jinja_env.globals['current_user_permissions'] = current_user_permissions
    app.jinja_env.globals['is_flag_enabled'] = is_flag_enabled
    # registra el blueprint de las rutas de administración.

    app.register_blueprint(auth_bp, url_prefix="/auth")
    #app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(user_admin_bp, url_prefix="/admin/users")
    app.register_blueprint(feature_flags_bp)

    app.register_blueprint(tag_bp, url_prefix="/tags")

    # app.register_blueprint(auth_bp, url_prefix="/auth")
    # app.register_blueprint(admin_bp, url_prefix="/admin")
    # app.register_blueprint(user_admin_bp, url_prefix="/admin/users")

    # define la ruta para la página principal.
    print("Conectando a:", config["production"].SQLALCHEMY_DATABASE_URI)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.cli.command("reset-db")
    def reset_db_command():
        reset_db()
        with app.app_context(): 
            seed_feature_flags()   
            seed_roles_permissions() 
            seed_admin_user()      
            print("Base de datos reseteada e inicializada con roles y admin.")

    @app.route("/limpiar_sesion")
    def limpiar_sesion():
        session.clear()
        return "Sesión borrada"
    
    @app.route("/maintenance/admin")
    def maintenance_admin():
        msg = g.feature_flags_msg.get("admin_maintenance_mode")
        return render_template(
            "maintenance_admin.html",
            message=msg or "El área de administración está en mantenimiento."
        )

    @app.route("/maintenance/portal")
    def maintenance_portal():
        msg = g.feature_flags_msg.get("portal_maintenance_mode")
        return render_template(
            "maintenance_portal.html",
            message=msg or "El portal está en mantenimiento."
        )
    maintenance_check(app)
    
    @app.context_processor
    def inject_flags():
        # Cargar flags de la BD
        flags = db.session.query(FeatureFlag).all()
        feature_flags = {f.key: f.is_enabled for f in flags}

        return {
            "feature_flags": feature_flags
        }
    return app

app = create_app()
with app.app_context():
    # Crea todas las tablas en la base de datos.
    db.create_all()
     # Lógica de siembra condicional: solo si no existe el rol principal
    admin_role = db.session.query(Role).filter_by(name="Administrador").first()
    if not admin_role:
        print("¡Base de datos vacía detectada! Inicializando roles y admin...")
        seed_roles_permissions() # Inserta Roles y Permisos
        seed_admin_user()        # Inserta el usuario Admin
        print("Inicialización completa. BD lista para usar.")


if __name__ == "__main__":

    app.run(debug=True)
    app.run(debug=True)
