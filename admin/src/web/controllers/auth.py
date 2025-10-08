from src.core.models.role_permission import Role
from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from src.core.user_service import authenticate_user, create_user
from src.core.permissions_service import get_role_by_name
from src.web.handlers.auth import login_required 
from src.web.handlers.maintenance import maintenance_protected

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route("/", methods=['GET'])
def login():
    """Maneja la visualización de la página de inicio de sesión.

    Esta función gestiona las peticiones GET a la ruta de inicio de sesión. 
    Antes de renderizar la plantilla de login, verifica si un usuario ya está 
    autenticado.

    Lógica:
    1. Comprueba si existe un 'user_id' en la sesión.
    2. Si el usuario ya está autenticado, redirige inmediatamente a la página 
       de inicio del administrador (`user_admin.home`).
    3. Si el usuario no está autenticado, renderiza el formulario de inicio de sesión.

    Returns:
        str: Redirección a la ruta de inicio (`user_admin.home`) si el usuario
             ya está en sesión, o la plantilla HTML renderizada ("login.html")
             en caso contrario.
    """
    if 'user_id' in session:
        return redirect(url_for("user_admin.home"))
    return render_template("login.html")


@auth_bp.route("/authenticate", methods=['POST'])
def authenticate():
    """Maneja el intento de autenticación del usuario a través de una petición POST.

    Esta función procesa el email y la contraseña enviados desde el formulario de login.

    Proceso de autenticación (POST):
    1. Obtiene el email y la contraseña del formulario.
    2. Llama a la función de servicio `authenticate_user` para validar las credenciales.
    3. Si la autenticación falla (el usuario no se encuentra o las credenciales son incorrectas):
       a. Muestra un mensaje flash de error y redirige de vuelta al formulario de login.
    4. Si la autenticación es exitosa (se devuelve el objeto `user`):
       a. Crea la sesión del usuario almacenando su ID, email, nombre y rol.
       b. Muestra un mensaje flash de bienvenida.
       c. Redirige a la página de inicio del administrador (`user_admin.home`).

    Returns:
        str: Redirección a la página de login si falla la autenticación, 
             o redirección a la página de inicio (`user_admin.home`) en caso de éxito.
    """
    email = request.form.get("email")
    password = request.form.get("password")

    user = authenticate_user(email, password)
    
    if not user:
        flash("Usuario o contraseña incorrecta.", "danger") 
        return redirect(url_for("auth.login")) 


    # Crea la sesión
    # Los datos del usuario se almacenan en el diccionario de la sesion
    session['user_id'] = user.id
    session['email'] = user.email
    session['nombre'] = f"{user.nombre}" 
    session['rol'] = user.rol
    
    flash(f"Bienvenido, {user.nombre}.", "success")
    return redirect(url_for("user_admin.home")) 


@auth_bp.route("/register", methods=['GET', 'POST'])
@maintenance_protected("admin")
def register():
    """Maneja el registro de nuevos usuarios públicos en el sistema.

    Esta función gestiona las peticiones GET para mostrar el formulario de registro y
    las peticiones POST para procesar la creación de una nueva cuenta. Está protegida
    por el decorador `maintenance_protected` para el rol "admin", lo que implica 
    que el registro se bloquea si el modo de mantenimiento está activo para ese rol.

    Flujo de la Función:
    1.  **Verificación de Sesión:** Si el usuario ya tiene un 'user_id' en la sesión, 
        se le redirige a la página de inicio (`user_admin.home`).
    2.  **Petición POST (Registro):**
        a.  Recupera `nombre`, `apellido`, `email` y `password` del formulario.
        b.  Obtiene el objeto `Role` correspondiente a "Usuario público" para asignar su `role_id` por defecto.
        c.  Intenta llamar a la función de servicio `create_user` con los datos, incluyendo `enabled=True`.
    3.  **Manejo de Errores:**
        a.  Si `create_user` tiene éxito, se muestra un mensaje flash de éxito y se redirige al login.
        b.  Si ocurre un `ValueError` (ej: email existente, validación de contraseña), se muestra el error específico al usuario.
        c.  Si ocurre cualquier otra `Exception`, se muestra un mensaje de error genérico.
    4.  **Petición GET:** Simplemente renderiza el formulario de registro (`register.html`).

    Returns:
        str: Redirección a la página de inicio si ya está autenticado, 
             redirección a la página de login en caso de registro exitoso, 
             o la plantilla 'register.html' (con o sin mensajes flash).
    """
    if 'user_id' in session:
        return redirect(url_for("user_admin.home"))
        
    if request.method == 'POST':
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        email = request.form.get("email")
        password = request.form.get("password")
        role_obj = get_role_by_name("Usuario público") 
        role_id = role_obj.id 
        print(role_id)
        try:
            # Chequeo de que el email no exista y creación del usuario.
            # La función create_user se encarga de hashear la contraseña.
            create_user({
                "nombre": nombre,
                "apellido": apellido,
                "email": email,
                "password": password,
                "role_id": role_id, # Asignación de rol por defecto
                "enabled": True
            })
            
            flash("Registro exitoso. ¡Inicia sesión!", "success")
            return redirect(url_for("auth.login"))

        except ValueError as e:
            # Captura errores como 'Email ya registrado' o validaciones internas
            flash(str(e), "danger") 
            return render_template("register.html")
        except Exception:
            flash("Ocurrió un error al intentar registrar el usuario.", "danger")
            return render_template("register.html")

    return render_template("register.html")


@auth_bp.route("/logout")
@login_required 
def logout():
    """Cierra la sesión del usuario actualmente autenticado.

    Esta función está protegida por el decorador `@login_required`, asegurando 
    que solo los usuarios con una sesión activa puedan acceder.

    Proceso:
    1.  Elimina todos los datos de la sesión del servidor (`session.clear()`).
    2.  Muestra un mensaje flash informativo indicando que la sesión ha sido cerrada.
    3.  Redirige al usuario a la página de inicio de sesión (`auth.login`).

    Returns:
        str: Redirección a la ruta de inicio de sesión.
    """
    # Clear elimina los datos del servidor
    session.clear() 
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for("auth.login"))