# archivo que contiene las funciones que interactúan con la bd para los usuarios
from src.core.models.user import User
from src.core.database import db
from werkzeug.security import generate_password_hash


def get_user_by_email(email):
    """
    Busca y retorna un usuario por su dirección de correo electrónico.
    """
    return db.session.query(User).filter_by(email=email).first()


def get_user_by_id(user_id):
    """
    Busca y retorna un usuario por su ID.
    """
    return db.session.get(User, user_id)


def create_user(data):
    """
    Crea un nuevo usuario con una contraseña encriptada.
    """
    # Encripta la contraseña antes de crear el objeto
    data["password"] = generate_password_hash(data["password"])

    new_user = User(**data)
    db.session.add(new_user)
    db.session.commit()
    return new_user


def update_user(user_id, data):
    """
    Actualiza la información de un usuario existente.
    """
    user = get_user_by_id(user_id)
    if user:
        # Actualiza los campos si están en el diccionario de datos
        for key, value in data.items():
            if key == "password":
                # Encripta la nueva contraseña
                setattr(user, key, generate_password_hash(value))
            else:
                setattr(user, key, value)
        db.session.commit()
    return user


def delete_user(user_id):
    """
    Elimina un usuario de la base de datos.
    """
    user = get_user_by_id(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return False
