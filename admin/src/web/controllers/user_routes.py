from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from src.core.database import db
from src.core.user_service import list_users, create_user, update_user, delete_user, get_user_by_id, get_user_by_email, check_email_unique
from src.web.handlers.auth import login_required, permission_required
from src.core.bcrypt import check_password   
from src.core.models.user import User    

user_admin_bp = Blueprint("user_admin", __name__, url_prefix="/admin/users")



# ruta de Login
# Esta ruta manejará la URL /admin/
@user_admin_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = get_user_by_email(email)

        # 1. 🔑 Verificación Completa:
        #    - Que el usuario exista.
        #    - Que el usuario esté ACTIVADO (enabled=True).
        #    - Que la contraseña coincida con el hash almacenado.
        # 1. 🔑 Verificación Completa:
        #    - Que el usuario exista.
        #    - Que el usuario esté ACTIVADO (enabled=True).
        #    - Que la contraseña coincida con el hash almacenado.
        if user and user.enabled and check_password(password, user.password):
            
            # Autenticación exitosa
            
            # Autenticación exitosa
            session["user_id"] = user.id
            
            # 2. 🎯 Asignación de Rol a la sesión (usando la relación .name)
            # Asumiendo que user.role es la relación al objeto Role
            session["user_role"] = user.role.name 
            
            # 2. 🎯 Asignación de Rol a la sesión (usando la relación .name)
            # Asumiendo que user.role es la relación al objeto Role
            session["user_role"] = user.role.name 

            # redirige a la página de inicio (home.html)
            return redirect(url_for("user_admin.home"))
        else:
            # Autenticación fallida o usuario inactivo
            # Autenticación fallida o usuario inactivo
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
        # ... (código que obtiene datos y verifica email existente, sin cambios)
        # ... (código que obtiene datos y verifica email existente, sin cambios)
        email = request.form.get("email")
        password = request.form.get("password")
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")

        # validación de campos requeridos (esta es la validación del controller, déjala)
        # validación de campos requeridos (esta es la validación del controller, déjala)
        if not all([email, password, nombre, apellido]):
            return render_template(
                "register.html", error="Todos los campos son obligatorios."
            )

        # verificar si el email ya existe (déjala)
        # verificar si el email ya existe (déjala)
        existing_user = get_user_by_email(email)
        if existing_user:
            return render_template(
                "register.html", error="El email ya está registrado."
            )

        # datos para la creación del usuario (incluye 'password', está correcto)
        # datos para la creación del usuario (incluye 'password', está correcto)
        data = {
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "password": password, 
            "rol": "Usuario público", 
            "password": password, 
            "rol": "Usuario público", 
            "activo": True,
        }
        # ⬇️ ---------------------- CAMBIO CRÍTICO AQUÍ ---------------------- ⬇️
        try:
            # Llamar a la función de servicio para crear el usuario
            create_user(data)

            # redirigir al login si es exitoso
            return redirect(url_for("user_admin.login"))
        
        except ValueError as e:
            # Captura el error de validación de user_service.py y lo muestra al usuario
            return render_template("register.html", error=str(e))
        
        # ⬆️ 

            # redirigir al login si es exitoso
            return redirect(url_for("user_admin.login"))
        
        except ValueError as e:
            # Captura el error de validación de user_service.py y lo muestra al usuario
            return render_template("register.html", error=str(e))
        
        # ⬆️ ------------------------------------------------------------------ ⬆️


    # mostrar el formulario de registro en una solicitud GET
    return render_template("register.html")


@user_admin_bp.route("/list", methods=["GET"])
@login_required
@permission_required("user_index")
def list():
    """
    Muestra el listado paginado de usuarios con filtros opcionales.

    Query Parameters:
        page (int): Número de página (por defecto 1).
        search_email (str, optional): Filtra usuarios por email.
        search_enabled (str, optional): Filtra usuarios por estado ('True' o 'False').

    Returns:
        Response: Renderiza la plantilla 'list.html' con los usuarios y la paginación.
    """
    page = request.args.get("page", 1, type=int)
    search_email = request.args.get("search_email")
    search_enabled = request.args.get("search_enabled")
    
    pagination = list_users(
        page=page,
        per_page=25,
        search_email=search_email,
        search_enabled=search_enabled,
    )
    users = pagination.items
    return render_template("list.html", users=users, pagination=pagination)



@user_admin_bp.route("/new", methods=["GET", "POST"])
@login_required
@permission_required("user_new")
def new():
    """
    Crea un nuevo usuario con rol 'Usuario público' y siempre activo.

    POST Form Data:
        nombre (str): Nombre del usuario.
        apellido (str): Apellido del usuario.
        email (str): Email del usuario.
        password (str): Contraseña del usuario.

    Returns:
        Response: Redirige a la lista de usuarios si se crea correctamente.
                  Renderiza 'create_user.html' si es GET o hay errores.
    """
    if request.method == "POST":
        data = {
            "nombre": request.form.get("nombre"),
            "apellido": request.form.get("apellido"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
            "rol": "Usuario público", 
            "activo": True            
        }
        try:
            create_user(data)
            flash("Usuario creado correctamente.", "success")
            return redirect(url_for("user_admin.list"))
        except ValueError as e:
            flash(str(e), "danger")
    return render_template("create_user.html")




@user_admin_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("user_update")
def edit(user_id):
    """
    Edita un usuario existente.

    Path Parameters:
        user_id (int): ID del usuario a editar.

    POST Form Data:
        nombre (str): Nuevo nombre.
        apellido (str): Nuevo apellido.
        email (str): Nuevo email.
        password (str, optional): Nueva contraseña.
        activo (bool, optional): Estado activo/bloqueado.

    Returns:
        Response: Redirige a la lista de usuarios si se actualiza correctamente.
                  Renderiza 'edit_user.html' si es GET o hay errores.
    """
    user = get_user_by_id(user_id)
    if not user:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("user_admin.list"))
    

    if request.method == "POST":
        data = {
            "nombre": request.form.get("nombre"),
            "apellido": request.form.get("apellido"),
            "email": request.form.get("email"),
            "enabled": True if request.form.get("activo") else False
        }

        password = request.form.get("password")
        if password:
            data["password"] = password
       
        if data['email'] != user.email:
            try:
                check_email_unique(data['email'], current_user_id=user_id)
            except ValueError as e:
                flash(str(e), "danger")
                return render_template("edit_user.html", user=user)
            
        try:
            update_user(user_id, data)
            flash("Usuario actualizado correctamente.", "success")
            return redirect(url_for("user_admin.list"))
        except ValueError as e:
            flash(str(e), "danger")
        
    return render_template("edit_user.html", user=user)





@user_admin_bp.route("/<int:user_id>/delete", methods=["POST"])
def delete(user_id):
    """
    Marca un usuario como eliminado.

    Path Parameters:
        user_id (int): ID del usuario a eliminar.

    Returns:
        Response: Redirige a la lista de usuarios mostrando mensaje de éxito o error.
    """
    user = get_user_by_id(user_id)
    if user:
        user.eliminado = True  
        db.session.commit()
        flash("Usuario eliminado correctamente", "success")
    else:
        flash("Usuario no encontrado", "error")
    return redirect(url_for("user_admin.list"))



@user_admin_bp.route("/<int:user_id>/toggle_enabled", methods=["POST"])
@login_required
@permission_required("user_update")
def toggle_enabled(user_id):
    """
    Alterna el estado activo/bloqueado de un usuario.

    Path Parameters:
        user_id (int): ID del usuario a modificar.

    Returns:
        Response: Redirige a la lista de usuarios mostrando mensaje de éxito o error.
    """
    user = get_user_by_id(user_id)
    if not user:
        flash("Usuario no encontrado.", "danger")
    elif getattr(user, "system_admin", False):
        flash("No se puede bloquear/desbloquear al administrador del sistema.", "danger")
    else:
        user.enabled = not user.enabled
        db.session.commit()
        estado = "activado" if user.enabled else "bloqueado"
        flash(f"Usuario {estado} correctamente.", "success")
    return redirect(url_for("user_admin.list"))