from src.core.database import db
from src.core.models.user import User
from src.core.models.role_permission import Role, Permission, RolePermission
from src.core.bcrypt import hash_password


def seed_roles_permissions():
    print("--- 1. Inicializando Roles y Permisos ---")

    # Roles
    admin_role = Role(name="Administrador")
    editor_role = Role(name="Editor")
    public_role = Role(name="Usuario público")

    roles = [admin_role, editor_role, public_role]

    # 2. Permisos
    permisos = [
        Permission(name="user_index"),
        Permission(name="user_new"),
        Permission(name="user_update"),
        Permission(name="user_destroy"),
        Permission(name="user_show"),
        Permission(name="tag_manage"),  # ejemplo adicional
    ]

    db.session.add_all(roles + permisos)
    db.session.commit()

    # 3. Asociar roles con permisos
    role_perm_map = {
        "Administrador": ["user_index", "user_new", "user_update", "user_destroy", "user_show", "tag_manage"],
        "Editor": ["tag_manage"],
        "Usuario público": []
    }

    for role_name, perm_names in role_perm_map.items():
        role = db.session.query(Role).filter_by(name=role_name).first()
        for perm_name in perm_names:
            perm = db.session.query(Permission).filter_by(name=perm_name).first()
            rp = RolePermission(role_id=role.id, permission_id=perm.id)
            db.session.add(rp)

    db.session.commit()
    print("Roles y permisos iniciales creados.")


def seed_admin_user():
    # Crear un admin inicial
    admin_role = db.session.query(Role).filter_by(name="Administrador").first()
    if not admin_role:
        raise ValueError("No se encontró el rol Administrador, corre seed_roles_permissions primero.")

    hashed_password = hash_password("admin123")  # contraseña inicial segura

    admin_user = User(
        nombre="Admin",
        apellido="Principal",
        email="admin@example.com",
        password=hashed_password.decode('utf-8'),
        role_id=admin_role.id,
        system_admin=True,
        enabled=True,
        eliminado=False
    )

    db.session.add(admin_user)
    db.session.commit()
    print("Usuario Administrador inicial creado: admin@example.com / admin123")


if __name__ == "__main__":
    with app.app_context():  # esto “activa” la app para poder usar db.session
        seed_roles_permissions()
        seed_admin_user()
