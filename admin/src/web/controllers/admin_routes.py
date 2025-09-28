from flask import Blueprint, render_template, request, redirect, url_for, session
from src.core.user_service import get_user_by_email, create_user

# crea una instancia del blueprint
admin_bp = Blueprint(
    "admin", __name__, url_prefix="/admin", template_folder="../templates"
)


# ruta de Login
# Esta ruta manejará la URL /admin/
@admin_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = get_user_by_email(email)

        if user and user.check_password(password):
            # autenticación exitosa
            session["user_id"] = user.id
            session["user_role"] = user.rol

            # redirige a la página de inicio (home.html)
            return redirect(url_for("admin.home"))
        else:
            # autenticación fallida
            return render_template(
                "login.html", error="Credenciales inválidas o cuenta inactiva."
            )

    return render_template("login.html")


# define la ruta de la página de inicio del admin
# esta ruta manejará la URL /admin/home
@admin_bp.route("/home")
def home():
    return render_template("home.html")


# ruta de Registro
@admin_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")

        # validación de campos requeridos
        if not all([email, password, nombre, apellido]):
            return render_template(
                "register.html", error="Todos los campos son obligatorios."
            )

        # verificar si el email ya existe
        existing_user = get_user_by_email(email)
        if existing_user:
            return render_template(
                "register.html", error="El email ya está registrado."
            )

        # datos para la creación del usuario
        data = {
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "password": password,
            "rol": "Usuario público",  # Rol por defecto
            "activo": True,
        }

        # Llamar a la función de servicio para crear el usuario
        # hacer que create_user maneje el hashing de la clave
        create_user(data)

        # redirigir al login
        return redirect(url_for("admin.login"))

    # mostrar el formulario de registro en una solicitud GET
    return render_template("register.html")
