from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from src.core.permissions_service import get_role_by_name
from src.core.user_service import authenticate_user, create_user
from src.web.handlers.auth import login_required
from src.web.handlers.maintenance import maintenance_protected
from src.web.user_validations import UserForm

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
    """Maneja el registro de nuevos usuarios públicos, con validación de WTForms."""
    
    # Redirigir si ya está logueado
    if 'user_id' in session:
        return redirect(url_for("user_admin.home"))

    #  Instanciar el formulario
    form = UserForm(request.form)

    #  Deshabilitar validadores para campos que no están en el formulario de registro 
    # (role_id y enabled se asignan por defecto y no son enviados por el formulario)
    form.role_id.validators = [] 
    form.enabled.validators = []
    
    if request.method == 'POST':
        # Ejecutar la validación de WTForms
        if form.validate_on_submit():
            # Los datos son válidos. Ahora intenta crear el usuario.
            try:
                # Obtener el rol por defecto (Usuario público)
                role_obj = get_role_by_name("Usuario público") 
                role_id = role_obj.id 

                # Llama al servicio con los datos VALIDADOS del formulario
                create_user({
                    "nombre": form.nombre.data,
                    "apellido": form.apellido.data,
                    "email": form.email.data,
                    "password": form.password.data,
                    "role_id": role_id, # Asignado por defecto
                    "enabled": True
                })
                
                flash("Registro exitoso. ¡Inicia sesión!", "success")
                return redirect(url_for("auth.login"))

            except ValueError as e:
                # Captura errores del servicio (ej: unicidad del email a nivel DB)
                flash(str(e), "danger") 
                # Si falla el servicio, se pasa el formulario al template para mostrar los datos ingresados.
            except Exception:
                flash("Ocurrió un error al intentar registrar el usuario.", "danger")
                
    #  Renderiza la plantilla (GET o POST fallido)
    # Pasa el objeto 'form' a la plantilla para que pueda mostrar los campos y los errores.
    return render_template("register.html", form=form)


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