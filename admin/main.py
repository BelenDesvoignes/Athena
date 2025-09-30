from flask import Flask, render_template, session
from src.web.config import config
from src.core.database import db, reset_db
from src.web.controllers.auth import auth_bp
from src.web.controllers.user_routes import user_admin_bp
from src.core.permissions_service import get_permissions_for_user
from src.core.user_service import get_user_by_id



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
    # define la ruta para la página principal.
    @app.route("/")
    def index():
        return render_template("home.html") 
    
    @app.context_processor
    def inject_permissions():
        permisos = []
        if 'user_id' in session:
            user = get_user_by_id(session['user_id'])
            if user:
                permisos = get_permissions_for_user(user)
        return dict(user_permisos=permisos)
    


    @app.cli.command("reset-db")
    def reset_db_command():
        reset_db()

    return app

  

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
