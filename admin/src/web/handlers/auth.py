from functools import wraps
from src.core.database import db
from flask import session, redirect, url_for, flash


def login_required(f):
    """Decorador que verifica si el usuario tiene una sesión activa."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder al área de administración.', 'danger')
            return redirect(url_for('auth.login')) 
        return f(*args, **kwargs)
    return decorated_function


def permission_required(permission_name: str):
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
                return redirect(url_for('admin.home'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

