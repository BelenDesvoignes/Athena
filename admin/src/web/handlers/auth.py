from functools import wraps
from flask import flash, redirect, session, url_for

from src.core.database import db



def login_required(f):
    """Verifica si el usuario tiene una sesión activa ('user_id' en la sesión).

    Este decorador se utiliza en rutas que requieren autenticación. Si el usuario 
    no tiene una sesión activa, interrumpe la ejecución de la función de vista 
    decorada y realiza los siguientes pasos:
    
    1. Muestra un mensaje flash de error indicando que se requiere iniciar sesión.
    2. Redirige al usuario a la ruta de inicio de sesión ('auth.login').

    Si la sesión existe, la función de vista original se ejecuta normalmente.

    Args:
        f (function): La función de vista (view function) a decorar.

    Returns:
        function: La función decorada que incluye la lógica de verificación de sesión.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder al área de administración.', 'danger')
            return redirect(url_for('auth.login')) 
        return f(*args, **kwargs)
    return decorated_function


def permission_required(permission_name: str):
    """Decorador de acceso basado en permisos, con doble anidación.

    Este decorador garantiza que solo los usuarios autenticados, cuyo rol tenga 
    el permiso específico requerido, puedan acceder a una función de vista (view function).

    Flujo de Verificación:
    1. **Autenticación:** Verifica si 'user_id' existe en la sesión. Si no, redirige 
       al login con un mensaje de error.
    2. **Existencia del Usuario:** Recupera el objeto User de la base de datos. Si 
       no se encuentra, redirige al login.
    3. **Verificación de Permiso:** Comprueba si `permission_name` está presente en la 
       lista de permisos asociados al rol del usuario. Si no lo está, redirige a 
       la página de inicio del administrador (`user_admin.home`) con una advertencia.
    4. **Acceso:** Si todas las verificaciones pasan, la función de vista original se ejecuta.

    Args:
        permission_name (str): El nombre del permiso que se requiere para acceder 
                               a la función de vista decorada (ej: 'user_index', 'site_delete').

    Returns:
        function: La función decorada que envuelve la función de vista.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debes iniciar sesión para acceder.', 'danger')
                return redirect(url_for('auth.login'))

            from src.core.models.user import User

            user_id = session.get('user_id')
            user = db.session.get(User, user_id)
            if not user:
                flash('Usuario no encontrado.', 'danger')
                return redirect(url_for('auth.login'))

            # todos los permisos del rol desde la BD
            role_permissions = [perm.name for perm in user.role.permissions]

            if permission_name not in role_permissions:
                flash('No tienes permisos para realizar esta acción.', 'warning')
                return redirect(url_for('user_admin.home'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

