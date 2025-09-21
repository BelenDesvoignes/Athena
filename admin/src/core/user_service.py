# archivo que contiene las funciones que interactúan con la bd para los usuarios
from src.core.database import db
from src.core.models.users import User



def get_user_by_email(email):
    """
    Busca un usuario por su email.
    
    Args:
        email: El email del usuario a buscar.
    
    Returns:
        User: El objeto usuario si existe, o None si no.
    """
    return db.session.query(User).filter_by(email=email).first()


def get_user_by_id(id):
    """
    Busca un usuario por su ID.
    
    Args:
        id: El ID del usuario.
        
    Returns:
        User: El objeto usuario si existe, o None si no.
    """
    return db.session.query(User).get(id)