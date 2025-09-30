from flask import Flask, render_template, session
from src.web.config import config
from src.core.database import db, reset_db
from src.web.controllers.auth import auth_bp
from src.web.controllers.user_routes import user_admin_bp
from src.core.seeds import seed_roles_permissions, seed_admin_user 


def create_app(env="development"):
    # configura la carpeta de archivos estáticos y la de plantillas.
    app = Flask(
        __name__, static_folder="src/web/static", template_folder="src/web/templates"
    )

    # carga la configuración del ambiente.
    app.config.from_object(config[env])

    # inicializa la base de datos con la aplicación.
    db.init_app(app)

    # registra el blueprint de las rutas de administración.

    app.register_blueprint(auth_bp, url_prefix="/auth")
    #app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(user_admin_bp, url_prefix="/admin/users")

    # app.register_blueprint(auth_bp, url_prefix="/auth")
    # app.register_blueprint(admin_bp, url_prefix="/admin")
    # app.register_blueprint(user_admin_bp, url_prefix="/admin/users")

    # define la ruta para la página principal.

    @app.route("/")
    def index():
        return render_template("home.html")

    @app.cli.command("reset-db")
    def reset_db_command():
        reset_db()
        with app.app_context(): 
            seed_roles_permissions() # <-- ¡CRÍTICO para insertar roles!
            seed_admin_user()        # <-- ¡CRÍTICO para crear el admin!
            print("Base de datos reseteada e inicializada con roles y admin.")

    return app


app = create_app()
with app.app_context():
    # crea todas las tablas en la base de datos.
    db.create_all()



app = create_app()
with app.app_context():
    # crea todas las tablas en la base de datos.
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
