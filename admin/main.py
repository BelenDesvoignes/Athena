from flask import Flask, render_template
from src.web.controllers.admin_routes import admin_bp
from src.web.config import config
from src.core.database import db, reset_db


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
    app.register_blueprint(admin_bp)

    # define la ruta para la página principal.
    @app.route("/")
    def index():
        return render_template("home.html")
    



    @app.cli.command("reset-db")
    def reset_db():
        db.reset_db()

    return app



if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        # crea todas las tablas en la base de datos.
        db.create_all()
    app.run(debug=True)
