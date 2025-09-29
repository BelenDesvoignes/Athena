# admin/src/core/user_service.py
from src.core.database import db
from src.core.models.user import User 
from werkzeug.security import generate_password_hash,check_password_hash
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.models.role_permission import Role


def get_user_by_email(email):
    """ Busca y retorna un usuario por su dirección de correo electrónico. """
    return db.session.query(User).filter_by(email=email).first()



def get_user_by_id(user_id):
    """ Busca y retorna un usuario por su ID. """
    # Usa la sintaxis moderna de SQLAlchemy
    return db.session.get(User, user_id) 



def check_email_unique(email, current_user_id=None):
    query = User.query.filter_by(email=email)
    if current_user_id:
        query = query.filter(User.id != current_user_id)
    
    if query.first():
        raise ValueError(f"El email '{email}' ya está registrado.")
    

 
def validate_data(data, is_new=True):

    nombre = data.get('nombre')
    apellido = data.get('apellido')
    email = data.get('email')
    password = data.get('password')
    role_id = data.get('role_id')

    if not nombre or not apellido or not email or not role_id:
        raise ValueError("Nombre, apellido, email y rol son obligatorios.")

    if is_new and not password:
        raise ValueError("La clave es obligatoria para nuevos usuarios.")

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Formato de email inválido.")

    if password and len(password) < 8:
        raise ValueError(f"La clave debe tener al menos 8 caracteres.")
    

    if not db.session.get(Role, int(role_id)):
        raise ValueError("El ID de rol proporcionado es inválido.")


def create_user(data):
    validate_data(data, is_new=True)
    check_email_unique(data['email'])

    hashed_password = generate_password_hash(data['password'])
    activo = data.get('enabled') == 'False' if data.get('enabled') is not None else False
    
    try:
        user = User(
            nombre=data['nombre'],
            apellido=data['apellido'],
            email=data['email'],
            password=hashed_password,
            role_id=int(data['role_id']),
            enbled=activo
        )
        db.session.add(user)
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Error al crear usuario en DB: {e}")


def update_user(user_id, data):
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado.")

    validate_data(data, is_new=False)
    
    if data['email'] != user.email:
        check_email_unique(data['email'], current_user_id=user_id)
    
   
    activo_nuevo = data.get('enabled') == 'False'
    
   
    if user.system_admin and activo_nuevo == False:
        raise ValueError("Error: Un usuario con rol de Administrador de Sistema no puede ser bloqueado.")

    try:
        user.nombre = data['nombre']
        user.apellido = data['apellido']
        user.email = data['email']
        user.role_id = int(data['role_id'])
        user.activo = activo_nuevo

        if data.get('password'):
            if len(data['password']) < 8:
                raise ValueError(f"La nueva clave debe tener al menos 8 caracteres.")
            user.password = generate_password_hash(data['password'])
        
        db.session.commit()
        return user
    except ValueError as ve:
        db.session.rollback()
        raise ve
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Error al actualizar usuario en DB: {e}")




def delete_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado.")
    
    if user.system_admin:
        raise ValueError("Error: Un usuario con rol de Administrador de Sistema no puede ser eliminado.")

    try:
        db.session.delete(user)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Error al eliminar usuario en DB: {e}")


def list_users(page, per_page, search_email=None, search_enabled=None, search_role_id=None, order_by='fecha_creacion', order_dir='desc'):
  
    query = User.query
    
    #por Email 
    if search_email:
        query = query.filter(User.email.ilike(f"%{search_email}%"))

    #Filtrado por estado 
    if search_enabled in ('True', 'False'):
        is_enabled = search_enabled == 'False'
        query = query.filter_by(enabled=is_enabled)

    # por Rol
    if search_role_id:
        try:
            role_id_int = int(search_role_id)
            query = query.filter_by(role_id=role_id_int)
        except ValueError:
            pass 

    # Ordenamiento fecha de creación
    if hasattr(User, order_by):
        column = getattr(User, order_by)
        if order_dir == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

    # 5. paginacion 
    return query.paginate(page=page, per_page=per_page, error_out=False)



def get_user_credentials(email, password):
   
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return None 

    if not user.activo:
        return 'BLOCKED' 

    if check_password_hash(user.password, password):
        return user 
    else:
        return None