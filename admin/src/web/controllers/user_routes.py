from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from src.core.database import db
from src.core.user_service import list_users, create_user, update_user, delete_user, get_user_by_id, get_user_by_email, check_email_unique
from src.web.handlers.auth import login_required, permission_required
from src.core.bcrypt import check_password   
from src.core.models.user import User    
from src.web.handlers.maintenance import maintenance_protected
user_admin_bp = Blueprint("user_admin", __name__, url_prefix="/admin/users")

# Ruta de Login
# Esta ruta maneja la URL /admin/
@user_admin_bp.route("/", methods=["GET", "POST"])
def login():
    """Maneja la autenticación de usuarios mediante correo electrónico y contraseña.

    Esta función gestiona las peticiones GET para mostrar el formulario de login 
    y las peticiones POST para procesar las credenciales.

    Proceso de autenticación (POST):
    1. Obtiene el email y la contraseña del formulario.
    2. Busca el usuario por email.
    3. Verifica que:
       a. El usuario exista (`user`).
       b. El usuario esté activo (`user.enabled`).
       c. La contraseña proporcionada coincida con el hash almacenado (`check_password`).
    4. Si la autenticación es exitosa, se establece `user_id` y `user_role` 
       en la sesión, y se redirige a la página de inicio.
    5. Si falla, se vuelve a renderizar el formulario con un mensaje de error.

    Returns:
        str: Redirección a la página de inicio en caso de éxito, 
             o la plantilla 'login.html' (con o sin error) en caso contrario.
    """
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = get_user_by_email(email)

        #  Se verifica
        #    - Que el usuario exista.
        #    - Que el usuario esté ACTIVADO (enabled=True).
        #    - Que la contraseña coincida con el hash almacenado.
        #  Se verifica
        #    - Que el usuario exista.
        #    - Que el usuario esté ACTIVADO (enabled=True).
        #    - Que la contraseña coincida con el hash almacenado.
        if user and user.enabled and check_password(password, user.password):
            
            # Autenticación exitosa
            session["user_id"] = user.id
            session["user_name"] = user.nombre
            session["user_apellido"] = user.apellido
            session["user_email"] = user.email
            session["user_enabled"] = user.enabled
            # Asignación de Rol a la sesión (usando la relación .name)
            session["user_role"] = user.role.name 
            
            return redirect(url_for("user_admin.home"))
        else:
            # Autenticación fallida o usuario inactivo
            return render_template(
                "login.html", error="Contraseña incorrecta o cuenta inactiva."
            )

    return render_template("login.html")


# Define la ruta de la página de inicio del admin
@user_admin_bp.route("/home")
def home():
    """
    Renderiza la página principal o de bienvenida del módulo de administración de usuarios.

    Esta función es accesible a través de la ruta '/home' dentro del blueprint 
    de administración de usuarios.

    Returns:
        str: La plantilla HTML renderizada ("home.html").
    """
    return render_template("home.html")


# Ruta de Registro
@user_admin_bp.route("/register", methods=["GET", "POST"])
@maintenance_protected("admin")
def register():
    """Maneja el registro de nuevos usuarios en el sistema.

    Esta función gestiona las peticiones GET para mostrar el formulario de registro 
    y las peticiones POST para procesar y crear una nueva cuenta. Está protegida 
    por el decorador `maintenance_protected` para el rol "admin".

    Proceso de registro (POST):
    1. Obtiene los campos necesarios (email, password, nombre, apellido) del formulario.
    2. Valida que todos los campos requeridos estén presentes.
    3. Verifica si ya existe un usuario con el email proporcionado.
    4. Si las validaciones son exitosas, prepara los datos con el rol "Usuario público" 
       y el estado `activo=True`.
    5. Llama al servicio `create_user` para persistir los datos.
    6. En caso de éxito, redirige a la página de inicio de sesión.
    7. En caso de error (p. ej., validación de contraseña en el servicio), captura 
       el `ValueError` y lo muestra al usuario en el formulario.

    Returns:
        str: Redirección a la página de login en caso de éxito, 
             o la plantilla 'register.html' (con mensaje de error) en caso contrario.
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")

        # Valida de campos requeridos 
        if not all([email, password, nombre, apellido]):
            return render_template(
                "register.html", error="Todos los campos son obligatorios."
            )

        # Verifica si el email ya existe 
        existing_user = get_user_by_email(email)
        if existing_user:
            return render_template(
                "register.html", error="El email ya está registrado."
            )

        # Datos para la creación del usuario 
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
        try:
            # Llama a la función de servicio para crear el usuario
            create_user(data)

            # Redirige al login si es exitoso
            return redirect(url_for("user_admin.login"))
        
        except ValueError as e:
            # Captura el error de validación de user_service.py y lo muestra al usuario
            return render_template("register.html", error=str(e))

            # Redirige al login si es exitoso
            return redirect(url_for("user_admin.login"))
        
        except ValueError as e:
            # Captura el error de validación de user_service.py y lo muestra al usuario
            return render_template("register.html", error=str(e))
        


    # Muestra el formulario de registro en una solicitud GET
    return render_template("register.html")

@maintenance_protected("admin")
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
    sort_by = request.args.get("sort_by")  # nuevo parámetro

    pagination = list_users(
        page=page,
        per_page=25,
        search_email=search_email,
        search_enabled=search_enabled,
        sort_by=sort_by
    )
    users = pagination.items

    return render_template("list.html", users=users, pagination=pagination)

@maintenance_protected("admin")
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


@maintenance_protected("admin")
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

@maintenance_protected("admin")
@user_admin_bp.route("/<int:user_id>/delete", methods=["POST"])
def delete(user_id):
    """
    Marca un usuario como eliminado con protección para el administrador del sistema.

    Path Parameters:
        user_id (int): ID del usuario a eliminar.

    Returns:
        Response: Redirige a la lista de usuarios mostrando mensaje de éxito o error.
    """
    try:
        # Llamamos a la función de negocio que maneja la validación
        delete_user(user_id)
        flash("Usuario eliminado correctamente", "success")
    except ValueError as e:
        # Capturamos el error si es admin o usuario no encontrado
        flash(str(e), "danger")
    
    return redirect(url_for("user_admin.list"))


@maintenance_protected("admin")
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
        flash("No se puede bloquear al administrador del sistema.", "danger")
    else:
        user.enabled = not user.enabled
        db.session.commit()
        estado = "activado" if user.enabled else "bloqueado"
        flash(f"Usuario {estado} correctamente.", "success")
    return redirect(url_for("user_admin.list"))

@user_admin_bp.route("/profile")
@login_required 
def profile():
    """
    Renderiza la página de perfil del usuario logueado. 
    Los datos se obtienen directamente de la variable 'session' para mayor velocidad.
    """
    return render_template("profile.html")

