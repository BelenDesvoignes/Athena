from src.core.database import db
from src.core.models.user import User
from src.core.models.role_permission import Role, Permission, RolePermission
from src.core.models.feature_flags import FeatureFlag
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
        Permission(name="tag_manage"),             # ejemplo adicional
        Permission(name="feature_flags_manage"),
        Permission(name="export_csv"),             # permiso extra agregado
    ]

    db.session.add_all(roles + permisos)
    db.session.commit()

    # 3. Asociar roles con permisos
    role_perm_map = {
        "Administrador": [
            "user_index",
            "user_new",
            "user_update",
            "user_destroy",
            "user_show",
            "tag_manage",
            "feature_flags_manage",
            "export_csv"
        ],
        "Editor": ["tag_manage", "export_csv"],
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

def seed_feature_flags():
    flags = [
        FeatureFlag(
            key="admin_maintenance_mode",
            display_name="Modo mantenimiento de administración",
            description="Deshabilita temporalmente el sitio de administración.",
            is_enabled=False,
            maintenance_message=None
        ),
        FeatureFlag(
            key="portal_maintenance_mode",
            display_name="Modo mantenimiento del portal web",
            description="Pone el portal en modo mantenimiento.",
            is_enabled=False,
            maintenance_message=None
        ),
        FeatureFlag(
            key="reviews_enabled",
            display_name="Permitir nuevas reseñas",
            description="Habilita o deshabilita la creación y visualización de reseñas en el portal.",
            is_enabled=True
        )
    ]

    db.session.add_all(flags)
    db.session.commit()
    print("Feature flags iniciales creados.")

#if __name__ == "__main__":
#    with app.app_context():  # esto “activa” la app para poder usar db.session
#        seed_roles_permissions()
#        seed_admin_user()
