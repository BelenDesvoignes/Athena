from src.core.database import db
from src.core.models.role_permission import Role
from src.core.models.user import User
from flask import session
import logging

logging.basicConfig(level=logging.DEBUG)


def get_role_by_name(role_name: str):
    """
    Busca y retorna un objeto Role a partir de su nombre.

    Args:
        role_name (str): Nombre del rol a buscar.

    Returns:
        Role: Objeto Role correspondiente al nombre dado.

    Raises:
        ValueError: Si no existe un rol con el nombre proporcionado.
    """
    role_obj = (
        db.session.execute(
            db.select(Role).filter_by(name=role_name)
        )
        .unique()  
        .scalar_one_or_none()
    )

    if role_obj is None:
        raise ValueError(f"El rol '{role_name}' no existe en la base de datos.")
    
    return role_obj




def current_user_permissions():
    """
    Obtiene la lista de nombres de permisos del usuario actualmente logueado.

    Retorna una lista vacía si no hay usuario en sesión o si el usuario no tiene rol.

    Returns:
        list[str]: Lista de nombres de permisos del usuario.
    """
    user_id = session.get("user_id")
    if not user_id:
        session.clear()
        return[]
    user = db.session.get(User, user_id)
    permisos = [perm.name for perm in user.role.permissions] if user and user.role else []
    logging.debug(f"Permisos del usuario {user.email}: {permisos}")
    return permisos