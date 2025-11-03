from geoalchemy2.elements import WKTElement

from src.core.bcrypt import hash_password
from src.core.database import db
from src.core.models.feature_flags import FeatureFlag
from src.core.models.role_permission import Permission, Role, RolePermission
from src.core.models.site import Sitio
from src.core.models.user import User




def seed_roles_permissions():
    print("--- 1. Inicializando Roles y Permisos ---")

    # Roles
    roles = ["Administrador", "Admin", "Editor", "Usuario público", "Moderador"]
    role_objs = []
    for r_name in roles:
        role = db.session.query(Role).filter_by(name=r_name).first()
        if not role:
            role = Role(name=r_name)
            db.session.add(role)
        role_objs.append(role)


    permisos_nombres = [
        "user_index", "user_new", "user_update", "user_destroy", "user_show",
        "tag_manage", "feature_flags_manage", "export_csv",
        "site_list", "site_detail", "site_new", "site_update", "site_delete", "user_moderation"
    ]
    permiso_objs = []
    for p_name in permisos_nombres:
        perm = db.session.query(Permission).filter_by(name=p_name).first()
        if not perm:
            perm = Permission(name=p_name)
            db.session.add(perm)
        permiso_objs.append(perm)

    db.session.commit()

    # Asignar permisos a roles
    role_perm_map = {
        "Administrador": permisos_nombres,
        "Admin": permisos_nombres,
        "Editor": ["tag_manage", "site_list", "site_detail", "site_new", "site_update"],
        "Usuario público": [],
        "Moderador": ["user_moderation"]
    }

    for role_name, perm_names in role_perm_map.items():
        role = db.session.query(Role).filter_by(name=role_name).first()
        for perm_name in perm_names:
            perm = db.session.query(Permission).filter_by(name=perm_name).first()
            # Evitar duplicados en RolePermission
            exists = db.session.query(RolePermission).filter_by(
                role_id=role.id, permission_id=perm.id
            ).first()
            if not exists:
                db.session.add(RolePermission(role_id=role.id, permission_id=perm.id))

    db.session.commit()
    print("Roles y permisos iniciales creados.")

def seed_admin_user():
    administrador_role = db.session.query(Role).filter_by(name="Admin").first()
    if not administrador_role:
        raise ValueError(
            "No se encontró el rol Admin, corre seed_roles_permissions primero."
        )
    hashed_password1 = hash_password("admin123")  
    admin_role = db.session.query(Role).filter_by(name="Administrador").first()
    if not admin_role:
        raise ValueError(
            "No se encontró el rol System Admin, corre seed_roles_permissions primero."
        )
    
    editor_role = db.session.query(Role).filter_by(name="Editor").first()
    if not editor_role:
        raise ValueError(
            "No se encontró el rol Editor, corre seed_roles_permissions primero."
        )
    hashed_password2 = hash_password("editor123")  

    hashed_password = hash_password("sysadmin123") 

    moderador_role = db.session.query(Role).filter_by(name="Moderador").first()
    if not moderador_role:
        raise ValueError(
            "No se encontró el rol Moderador, corre seed_roles_permissions primero."
        )
    hashed_password3 = hash_password("moderador123")  


    admin_user = User(
        nombre="Admin", 
        apellido="Principal",
        email="sysadmin@example.com",
        password=hashed_password.decode("utf-8"),
        role_id=admin_role.id,
        system_admin=True,
        enabled=True,
        eliminado=False,
    )

    administrador_user = User(
        nombre="Administrador", 
        apellido="Principal",
        email="admin@example.com",
        password=hashed_password1.decode("utf-8"),
        role_id=administrador_role.id,
        system_admin=False,
        enabled=True,
        eliminado=False,
    )

    editor_user = User(
        nombre="Editor",
        apellido="Principal",
        email="usuarioEditor@gmail.com",
        password=hashed_password2.decode("utf-8"),
        role_id=editor_role.id,
        system_admin=False, 
        enabled=True,
        eliminado=False,
    )

    moderador_user = User(
        nombre="Moderador",
        apellido="Principal",
        email="moderador@gmail.com",
        password=hashed_password3.decode("utf-8"),
        role_id=moderador_role.id,      
        system_admin=False,
        enabled=True,
        eliminado=False,        
    )

    db.session.add_all([admin_user, administrador_user, editor_user, moderador_user])
    db.session.commit()
    print("Usuario System Admin inicial creado: sysadmin@example.com / sysadmin123")
    print("Usuario Administrador inicial creado: admin@example.com / admin123")
    print("Usuario Editor inicial creado: usuarioEditor@gmail.com / editor123")
    print("Usuario Moderador inicial creado: moderador@gmail.com / moderador123")

def seed_sitios():
    # 🔑 CORRECCIÓN: SOLO SEMBRAR SI NO HAY SITIOS
    if db.session.query(Sitio).count() > 0:
        print("Sitios ya existentes. Omitiendo siembra.")
        return

    sitios = [
        Sitio(
            nombre="Cabildo de Buenos Aires",
            descripcion_breve="Edificio histórico en el centro de la ciudad.",
            descripcion_completa="El Cabildo fue sede del gobierno colonial y escenario de la Revolución de Mayo.",
            ciudad="Buenos Aires",
            provincia="Buenos Aires",
            estado_conservacion="Bueno",
            inauguracion=1810,
            categoria="Edificio público",
            visible=True,
            ubicacion=WKTElement('Point(-58.3702 -34.6083)', srid=4326),
        ),
        Sitio(
            nombre="Ruinas de San Ignacio",
            descripcion_breve="Reducción jesuítica en Misiones.",
            descripcion_completa="Las ruinas de San Ignacio son Patrimonio Mundial y muestran la historia de los jesuitas en Argentina.",
            ciudad="San Ignacio",
            provincia="Misiones",
            estado_conservacion="Regular",
            inauguracion=1632,
            categoria="Patrimonio Mundial",
            visible=True,
            ubicacion=WKTElement('Point(-55.5306 -27.2556)', srid=4326),
        ),
        Sitio(
            nombre="Casa Histórica de Tucumán",
            descripcion_breve="Lugar de la declaración de la independencia.",
            descripcion_completa="En esta casa se firmó la independencia argentina el 9 de julio de 1816.",
            ciudad="San Miguel de Tucumán",
            provincia="Tucumán",
            estado_conservacion="Bueno",
            inauguracion=1762,
            categoria="Museo",
            visible=True,
            ubicacion=WKTElement('Point(-65.2226 -26.8241)', srid=4326),
        ),
        # --- NUEVOS SITIOS AGREGADOS ---
        Sitio(
            nombre="Quebrada de Humahuaca",
            descripcion_breve="Paisaje natural y cultural en el Noroeste argentino.",
            descripcion_completa="Es un valle de montaña de 155 km de extensión, declarado Patrimonio de la Humanidad por la UNESCO.",
            ciudad="Humahuaca",
            provincia="Jujuy",
            estado_conservacion="Excelente",
            inauguracion=1, # <--- CORREGIDO: Asignamos 1 para sitios naturales
            categoria="Patrimonio Natural",
            visible=True,
            ubicacion=WKTElement('Point(-65.35 -23.35)', srid=4326),
        ),
        Sitio(
            nombre="Glaciar Perito Moreno",
            descripcion_breve="Impresionante masa de hielo en la Patagonia.",
            descripcion_completa="Ubicado en el Parque Nacional Los Glaciares, famoso por sus rupturas cíclicas.",
            ciudad="El Calafate",
            provincia="Santa Cruz",
            estado_conservacion="Excelente",
            inauguracion=1, # <--- CORREGIDO: Asignamos 1 para sitios naturales
            categoria="Patrimonio Natural",
            visible=True,
            ubicacion=WKTElement('Point(-73.04 -50.48)', srid=4326),
        ),
        Sitio(
            nombre="Manzana Jesuítica",
            descripcion_breve="Conjunto arquitectónico jesuita en Córdoba.",
            descripcion_completa="Declarado Patrimonio de la Humanidad, incluye la Iglesia de la Compañía de Jesús y la Universidad Nacional de Córdoba.",
            ciudad="Córdoba",
            provincia="Córdoba",
            estado_conservacion="Bueno",
            inauguracion=1600,
            categoria="Patrimonio Mundial",
            visible=True,
            ubicacion=WKTElement('Point(-64.1873 -31.4173)', srid=4326),
        ),
    ]
    db.session.add_all(sitios)
    db.session.commit()
    print("Sitios históricos de ejemplo cargados.")

def seed_feature_flags():
    flags = [
        {
            "key": "admin_maintenance_mode",
            "display_name": "Modo mantenimiento de administración",
            "description": "Deshabilita temporalmente el sitio de administración.",
            "is_enabled": False,
            "maintenance_message": None
        },
        {
            "key": "portal_maintenance_mode",
            "display_name": "Modo mantenimiento del portal web",
            "description": "Pone el portal en modo mantenimiento.",
            "is_enabled": False,
            "maintenance_message": None
        },
        {
            "key": "reviews_enabled",
            "display_name": "Permitir nuevas reseñas",
            "description": "Habilita o deshabilita la creación y visualización de reseñas en el portal.",
            "is_enabled": True,
            "maintenance_message": None
        }
    ]

    for f in flags:
        exists = db.session.query(FeatureFlag).filter_by(key=f["key"]).first()
        if not exists:
            db.session.add(FeatureFlag(**f))

    db.session.commit()
    print("Feature flags iniciales creados.")


#if __name__ == "__main__":
#    with app.app_context():  # esto “activa” la app para poder usar db.session
#        seed_roles_permissions()
#        seed_sitios()
#        seed_admin_user()
