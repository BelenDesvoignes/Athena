from flask import Flask, render_template, session
from src.web.config import config
from src.core.database import db, reset_db
from src.core.permissions_service import current_user_permissions
from src.web.controllers.auth import auth_bp
from src.web.controllers.user_routes import user_admin_bp
from src.web.controllers.tag_routes import tag_bp
from src.core.seeds import seed_roles_permissions, seed_admin_user 
from src.web.config import config


def create_app(env="development", static_folder="../../static"):
    # configura la carpeta de archivos estáticos y la de plantillas.
    
    app = Flask(
        __name__, static_folder=static_folder, template_folder="src/web/templates"
    )
    # carga la configuración del ambiente.
    app.config.from_object(config[env])

    # inicializa la base de datos con la aplicación.
    db.init_app(app)
    app.jinja_env.globals['current_user_permissions'] = current_user_permissions

    # registra el blueprint de las rutas de administración.

    app.register_blueprint(auth_bp, url_prefix="/auth")
    #app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(user_admin_bp, url_prefix="/admin/users")

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
            seed_roles_permissions() # <-- ¡CRÍTICO para insertar roles!
            seed_admin_user()        # <-- ¡CRÍTICO para crear el admin!
            print("Base de datos reseteada e inicializada con roles y admin.")

    @app.route("/limpiar_sesion")
    def limpiar_sesion():
        session.clear()
        return "Sesión borrada"
    return app

    

app = create_app()
with app.app_context():
    # crea todas las tablas en la base de datos.
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
