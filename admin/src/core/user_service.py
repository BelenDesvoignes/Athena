# archivo que contiene las funciones que interactúan con la bd para los usuarios
from src.core.database import db
from src.core.models.users import User
from werkzeug.security import generate_password_hash
import re

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


def create_user(nombre, apellido, email, password, rol="Usuario público", activo=True):
    validate_user_data(nombre, apellido, email, password, rol, activo)

    if get_user_by_email(email):
        raise ValueError(f"Email {email} ya registrado")

    user = User(nombre, apellido, email, password, rol, activo)
    db.session.add(user)
    db.session.commit()
    return user

def update_user(user_id, nombre=None, apellido=None, email=None, password=None, rol=None, activo=None):
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")

    if email and email != user.email and get_user_by_email(email):
        raise ValueError(f"Email {email} ya registrado")

   
    validate_user_update(
        nombre=nombre or user.nombre,
        apellido=apellido or user.apellido,
        email=email or user.email,
        password=password, 
        rol=rol or user.rol,
        activo=activo if activo is not None else user.activo
    )

    # ... (El resto de la asignación y commit está bien) ...
    if nombre: user.nombre = nombre
    if apellido: user.apellido = apellido
    if email: user.email = email
    if password: user.password = generate_password_hash(password)
    if rol: user.rol = rol
    if activo is not None: user.activo = activo

    db.session.commit()
    return user


def get_users(email=None, rol=None, activo=None, page=1, per_page=25, order_by="fecha_creacion", desc=False):
    query = db.session.query(User)
    
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if rol:
        query = query.filter_by(rol=rol)
    if activo is not None:
        query = query.filter_by(activo=activo)
    
    order_column = getattr(User, order_by)
    if desc:
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column)
    
    return query.offset((page-1)*per_page).limit(per_page).all()




def delete_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")
    db.session.delete(user)
    db.session.commit()


def get_users_by_email(email):
    return db.session.query(User).filter(User.email.ilike(f"%{email}%")).all()


def get_users_by_rol(rol):
    return db.session.query(User).filter_by(rol=rol).all()


def get_users_by_activo(activo):
    return db.session.query(User).filter_by(activo=activo).all()

def validate_user_data(nombre, apellido, email, password, rol, activo):
    if not nombre or not apellido or not email or not password:
        raise ValueError("Todos los campos requeridos deben completarse")

  
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Formato de email inválido")
    if len(password) < 8: 
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    if rol not in ["Usuario público", "Editor", "Administrador"]:
        raise ValueError("Rol inválido")
    if not isinstance(activo, bool):
        raise ValueError("El campo 'activo' debe ser True o False")


def validate_user_update(nombre, apellido, email, password, rol, activo):
    if not nombre or not apellido or not email:
        raise ValueError("Nombre, apellido y email son campos obligatorios.")

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Formato de email inválido.")

   
    if password:
        if len(password) < 8:
            raise ValueError("La nueva contraseña debe tener al menos 8 caracteres.")

    if rol not in ["Usuario público", "Editor", "Administrador"]:
        raise ValueError("Rol inválido.")

    if not isinstance(activo, bool):
        raise ValueError("El campo 'activo' debe ser True o False.")


def create_user(nombre, apellido, email, password, rol="Usuario público", activo=True):
    validate_user_data(nombre, apellido, email, password, rol, activo)

    if get_user_by_email(email):
        raise ValueError(f"Email {email} ya registrado")

    user = User(nombre, apellido, email, password, rol, activo)
    db.session.add(user)
    db.session.commit()
    return user