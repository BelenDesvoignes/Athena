# admin/src/core/user_service.py
from src.core.database import db
from src.core.models.user import User 
from datetime import datetime, timezone

from src.core.bcrypt import check_password, hash_password
from src.core.models.role_permission import Role


def get_user_by_email(email):
    """
    Retorna un usuario activo no eliminado por email.

    Args:
        email (str): Email del usuario a buscar.

    Returns:
        User: Instancia del usuario si existe y está activo, sino None.
    """
    return db.session.query(User).filter_by(email=email, eliminado=False).first()


def get_user_by_id(user_id):
    """
    Busca y retorna un usuario activo por su ID.

    Args:
        user_id (int): ID del usuario.

    Returns:
        User: Instancia del usuario si existe y está activo, sino None.
    """
    return db.session.query(User).filter_by(id=user_id, eliminado=False).first()


def check_email_unique(email, current_user_id=None):
    """
    Verifica que no exista un usuario activo con el mismo email.
    
    Args:
        email (str): Email a validar.
        current_user_id (int, optional): ID del usuario actual para ignorarlo en la verificación.

    Raises:
        ValueError: Si ya existe un usuario activo con el mismo email.
    """
    query = db.session.query(User).filter_by(email=email, eliminado=False)
    if current_user_id:
        query = query.filter(User.id != current_user_id)
    existing = query.first()
    if existing:
        raise ValueError("El email ya está registrado.")
 

def validate_data(data, is_new=True):
    """
    Valida los datos de un usuario antes de crear o actualizar.

    Args:
        data (dict): Diccionario con los campos 'nombre', 'apellido', 'email', 'password', 'rol'.
        is_new (bool): Indica si es un usuario nuevo.

    Raises:
        ValueError: Si faltan campos obligatorios o el formato de email/contraseña es inválido.
    """

    nombre = data.get('nombre')
    apellido = data.get('apellido')
    email = data.get('email')
    password = data.get('password')
    rol = data.get('rol')

    if not nombre or not apellido or not email or not rol:
        raise ValueError("Nombre, apellido, email son obligatorios.")

    if is_new and not password:
        raise ValueError("La clave es obligatoria para nuevos usuarios.")

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Formato de email inválido.")

    if password and len(password) < 8:
        raise ValueError(f"La clave debe tener al menos 8 caracteres.")
    


def create_user(data):
    """
    Crea un nuevo usuario en la base de datos.

    Args:
        data (dict): Diccionario con los campos 'nombre', 'apellido', 'email', 'password', 'rol'.

    Returns:
        User: Instancia del usuario creado.

    Raises:
        ValueError: Si los datos son inválidos o hubo error al guardar.
    """
    validate_data(data, is_new=True)
    check_email_unique(data['email'])

    role_obj = get_role_by_name(data['rol'])
    if not role_obj:
        raise ValueError(f"El rol '{data['rol']}' no existe.")

    hashed_password = hash_password(data['password']).decode('utf-8')

    try:
        user = User(
            nombre=data['nombre'],
            apellido=data['apellido'],
            email=data['email'],
            password=hashed_password,
            role_id=role_obj.id,
            enabled=True  
        )
        db.session.add(user)
        db.session.commit()
        return user
    except Exception:
        db.session.rollback()
        raise ValueError("Error al crear usuario en la base de datos.")



def update_user(user_id, data):
    """
    Actualiza los datos de un usuario existente.

    Args:
        user_id (int): ID del usuario a actualizar.
        data (dict): Diccionario con los campos a actualizar.

    Returns:
        User: Usuario actualizado.

    Raises:
        ValueError: Si el usuario no existe, email duplicado, contraseña inválida o error en la DB.
    """
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado.")

    # Validación de email
    if data['email'] != user.email:
        check_email_unique(data['email'], current_user_id=user_id)

    try:
        user.nombre = data['nombre']
        user.apellido = data['apellido']
        user.email = data['email']
        user.enabled = data.get('enabled', True)

        if data.get('password'):
            if len(data['password']) < 8:
                raise ValueError("La nueva clave debe tener al menos 8 caracteres.")
            user.password = hash_password(data['password'])
        
        user.fecha_actualizacion = datetime.now(timezone.utc)
        
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Error al actualizar usuario: {e}")




def delete_user(user_id):
    """
    Marca un usuario como eliminado.

    Args:
        user_id (int): ID del usuario a eliminar.

    Returns:
        User: Usuario eliminado (marcado).

    Raises:
        ValueError: Si el usuario no existe o es administrador del sistema.
    """
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("Usuario no encontrado.")
    
    if getattr(user, "system_admin", False) or user.role.name in ["Administrador", "Admin"]:
        raise ValueError("No se puede eliminar un usuario administrador del sistema.")

    user.eliminado = True
    print(f"Antes de commit: {user.id=} {user.eliminado=}")
    db.session.commit()
    print(f"Después de commit: {user.id=} {user.eliminado=}")
    
    return user

    

def list_users(page, per_page, search_email=None, search_enabled=None, sort_by=None):
    """
    Lista usuarios con paginación y filtros opcionales.

    Args:
        page (int): Número de página.
        per_page (int): Cantidad de usuarios por página.
        search_email (str, optional): Filtra por email.
        search_enabled (str, optional): Filtra por estado ('True' o 'False').

    Returns:
        Pagination: Objeto con atributos 'items', 'page', 'per_page', 'total', 'pages'.
    """
    query = db.session.query(User).filter_by(eliminado=False)

    if search_email:
        query = query.filter(User.email.ilike(f"%{search_email}%"))

    if search_enabled in ('True', 'False'):
        is_enabled = search_enabled == 'True'
        query = query.filter_by(enabled=is_enabled)

  
    if sort_by == "created":
        query = query.order_by(User.fecha_creacion.desc())  
    elif sort_by == "modified":
        query = query.order_by(User.fecha_actualizacion.desc())
    else:
        query = query.order_by(User.id.asc())  

   
    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()

    class Pagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page

    return Pagination(users, page, per_page, total)



def get_user_credentials(email, password):
    """
    Verifica credenciales de usuario para login.

    Args:
        email (str): Email del usuario.
        password (str): Contraseña a validar.

    Returns:
        User: Retorna la instancia del usuario si es válido, 'BLOCKED' si está bloqueado, o None si no coincide.
    """
   
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return None 

    if not user.enabled:
        return 'BLOCKED' 

    if check_password(user.password, password):
        return user 
    else:
        return None



def authenticate_user(email, password):
    user = db.session.query(User).filter_by(email=email).first()
    if user and check_password(password, user.password):
        return user
    return None



def get_role_by_name(name):
    """
    Busca y retorna un objeto Role por su nombre.

    Args:
        name (str): Nombre del rol.

    Returns:
        Role: Instancia del rol si existe, sino None.
    """
    return db.session.query(Role).filter_by(name=name).first()
