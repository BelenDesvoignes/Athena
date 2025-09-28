from functools import wraps
from flask import session, redirect, url_for, flash

# Diccionario de permisos simplificado
PERMISSIONS = {
    'Administrador': [
        'user_index', 'user_new', 'user_update', 'user_destroy', 'tag_manage'
    ],
    'Editor': [
        'tag_manage'
    ],
    'Usuario público': []
}

def login_required(f):
    """Decorador que verifica si el usuario tiene una sesión activa."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder al área de administración.', 'danger')
            return redirect(url_for('auth.login')) 
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission_key: str):
    """Decorador que verifica si el rol del usuario tiene un permiso específico."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debes iniciar sesión para acceder.', 'danger')
                return redirect(url_for('auth.login'))
            
            user_role = session.get('rol') 
            role_permissions = PERMISSIONS.get(user_role, [])
            
            if permission_key not in role_permissions:
                flash('No tienes los permisos necesarios para realizar esta acción.', 'warning')
                return redirect(url_for('home')) 
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator