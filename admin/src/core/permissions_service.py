from src.core.database import db
from src.core.models.role_permission import Role


def get_role_by_name(role_name: str):
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




def get_permissions_for_user(user):
    return [perm.name for perm in user.role.permissions]