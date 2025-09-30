from flask import Blueprint, render_template, request, redirect, url_for, flash,  session
from src.core.user_service import list_users, create_user, update_user, delete_user, get_user_by_id, get_user_by_email
from src.web.handlers.auth import login_required, permission_required

user_admin_bp = Blueprint("user_admin", __name__, url_prefix="/admin/users")



# ruta de Login
# Esta ruta manejará la URL /admin/
@user_admin_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = get_user_by_email(email)

        if user and user.password == password:
            # autenticación exitosa
            session["user_id"] = user.id
            session["user_role"] = user.rol

            # redirige a la página de inicio (home.html)
            return redirect(url_for("user_admin.home"))
        else:
            # autenticación fallida
            return render_template(
                "login.html", error="Credenciales inválidas o cuenta inactiva."
            )

    return render_template("login.html")


# define la ruta de la página de inicio del admin
# esta ruta manejará la URL /admin/home
@user_admin_bp.route("/home")
def home():
    return render_template("home.html")


# ruta de Registro
@user_admin_bp.route("/register", methods=["GET", "POST"])
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
        return redirect(url_for("user_admin.login"))

    # mostrar el formulario de registro en una solicitud GET
    return render_template("register.html")



@user_admin_bp.route("/list", methods=["GET"])
@login_required
@permission_required("user_index")
def list():
    page = request.args.get("page", 1, type=int)
    search_email = request.args.get("email")
    search_enabled = request.args.get("enabled")
    search_role_id = request.args.get("role_id")
    order_by = request.args.get("order_by", "fecha_creacion")
    order_dir = request.args.get("order_dir", "desc")
    
    pagination = list_users(
        page=page,
        per_page=25,
        search_email=search_email,
        search_enabled=search_enabled,
        search_role_id=search_role_id,
        order_by=order_by,
        order_dir=order_dir
    )
    users = pagination.items
    
    return render_template("list.html", users=users, pagination=pagination)


# Crear usuario
@user_admin_bp.route("/new", methods=["GET", "POST"])
@login_required
@permission_required("user_new")
def new():
    if request.method == "POST":
        data = {
            "nombre": request.form.get("nombre"),
            "apellido": request.form.get("apellido"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
            "role_id": request.form.get("role_id"),
            "enabled": request.form.get("enabled") == "True"
        }
        try:
            create_user(data)
            flash("Usuario creado correctamente.", "success")
            return redirect(url_for("user_admin.index"))
        except ValueError as e:
            flash(str(e), "danger")
    return render_template("form.html", user=None)



#detalle de usuario 
@user_admin_bp.route("/<int:user_id>", methods=["GET"]) 
@login_required 
@permission_required("user_show") 
def show(user_id): 
    user = get_user_by_id(user_id) 
    if not user: 
        flash("Usuario no encontrado.", "danger") 
        return redirect(url_for("user_admin.index")) 
    return render_template("show.html", user=user)


# Editar usuario
@user_admin_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("user_update")
def edit(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("user_admin.index"))

    if request.method == "POST":
        data = {
            "nombre": request.form.get("nombre"),
            "apellido": request.form.get("apellido"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
            "role_id": request.form.get("role_id"),
            "enabled": request.form.get("enabled") == "True"
        }
        try:
            update_user(user_id, data)
            flash("Usuario actualizado correctamente.", "success")
            return redirect(url_for("user_admin.index"))
        except ValueError as e:
            flash(str(e), "danger")
    return render_template("form.html", user=user)


# Eliminar usuario
@user_admin_bp.route("/<int:user_id>/delete", methods=["POST"])
@login_required
@permission_required("user_destroy")
def delete(user_id):
    user = get_user_by_id(user_id)  
    if not user:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("user_admin.index"))


    if user.role.name == "Administrador":
        flash("No se puede eliminar un usuario Administrador.", "danger")
        return redirect(url_for("user_admin.index"))
    try:
        delete_user(user_id)
        flash("Usuario eliminado correctamente.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("user_admin.index"))
