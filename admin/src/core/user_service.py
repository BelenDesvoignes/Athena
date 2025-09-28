# admin/src/core/user_service.py

from src.core.database import db
from src.core.models.user import User 
from werkzeug.security import generate_password_hash
import re


def get_user_by_email(email):
    """ Busca y retorna un usuario por su dirección de correo electrónico. """
    return db.session.query(User).filter_by(email=email).first()


def get_user_by_id(user_id):
    """ Busca y retorna un usuario por su ID. """
    # Usa la sintaxis moderna de SQLAlchemy
    return db.session.get(User, user_id) 



def validate_user_data(nombre, apellido, email, password, rol, activo):
    """ Validación para la creación (password obligatoria). """
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
    """ Validación para la actualización (password opcional). """
    if not nombre or not apellido or not email:
        raise ValueError("Nombre, apellido y email son campos obligatorios.")

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Formato de email inválido.")

    if password: # Solo valida si se proporciona una nueva contraseña
        if len(password) < 8:
            raise ValueError("La nueva contraseña debe tener al menos 8 caracteres.")

    if rol not in ["Usuario público", "Editor", "Administrador"]:
        raise ValueError("Rol inválido.")

    if not isinstance(activo, bool):
        raise ValueError("El campo 'activo' debe ser True o False")



def create_user(nombre, apellido, email, password, rol="Usuario público", activo=True):
    """ Crea un nuevo usuario. """
    validate_user_data(nombre, apellido, email, password, rol, activo)

    if get_user_by_email(email):
        raise ValueError(f"Email {email} ya registrado")

    hashed_password = generate_password_hash(password)
    
    user = User(nombre=nombre, apellido=apellido, email=email, password=hashed_password, rol=rol, activo=activo)
    
    db.session.add(user)
    db.session.commit()
    return user


def update_user(user_id, nombre=None, apellido=None, email=None, password=None, rol=None, activo=None):
    """ Actualiza un usuario existente. """
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

    # Aplicar los cambios
    if nombre is not None: user.nombre = nombre
    if apellido is not None: user.apellido = apellido
    if email is not None: user.email = email
    if password: user.password = generate_password_hash(password)
    if rol is not None: user.rol = rol
    if activo is not None: user.activo = activo

    db.session.commit()
    return user


def get_users(email=None, rol=None, activo=None, page=1, per_page=25, order_by="fecha_creacion", desc=False):
    """ Busca, filtra, ordena y pagina usuarios. Retorna (users, total_records). """
    query = db.session.query(User)
    
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if rol:
        query = query.filter_by(rol=rol)
    if activo is not None:
        query = query.filter_by(activo=activo)
    
    # Obtener el total de registros antes de aplicar paginación
    total_records = query.count()
    
    # Ordenación
    order_column = getattr(User, order_by)
    if desc:
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column)
    
    # Paginación
    users = query.offset((page-1)*per_page).limit(per_page).all()
    
    return users, total_records # Retornamos la lista y el total

def delete_user(user_id):
    """ Elimina un usuario. """
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado")
    db.session.delete(user)
    db.session.commit()
    return True

# Funciones de búsqueda específicas (opcionales, mantenidas por si acaso)
def get_users_by_email(email):
    return db.session.query(User).filter(User.email.ilike(f"%{email}%")).all()

def get_users_by_rol(rol):
    return db.session.query(User).filter_by(rol=rol).all()

def get_users_by_activo(activo):
    return db.session.query(User).filter_by(activo=activo).all()