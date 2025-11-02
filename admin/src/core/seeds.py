from geoalchemy2.elements import WKTElement

from src.core.bcrypt import hash_password
from src.core.database import db
from src.core.models.feature_flags import FeatureFlag
from src.core.models.role_permission import Permission, Role, RolePermission
from src.core.models.site import Sitio
from src.core.models.user import User
from datetime import datetime




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
        # 5 SITIOS CON FECHA EXPLÍCITA (PARA PROBAR ORDENAMIENTO) ---
        Sitio(
            nombre="La Recoleta (Vieja)", descripcion_breve="Cementerio con arte funerario.",
            descripcion_completa="...", ciudad="Buenos Aires", provincia="Buenos Aires", 
            estado_conservacion="Excelente", inauguracion=1822, categoria="Cultural", 
            visible=True, registrado=datetime(2022, 7, 1), # <-- Fecha antigua
            ubicacion=WKTElement('Point(-58.3800 -34.5800)', srid=4326)
        ),
        Sitio(
            nombre="Sitio Arqueológico El Shincal (Viejo)", descripcion_breve="Ruinas incas en Catamarca.", 
            descripcion_completa="...", ciudad="Londres", provincia="Catamarca", 
            estado_conservacion="Regular", inauguracion=1400, categoria="Ruinas", 
            visible=True, registrado=datetime(2022, 9, 10), # <-- Fecha antigua
            ubicacion=WKTElement('Point(-67.5000 -28.0000)', srid=4326)
        ),
        Sitio(
            nombre="Casa de Sarmiento (Vieja)", descripcion_breve="Casa natal del expresidente.", 
            descripcion_completa="...", ciudad="San Juan", provincia="San Juan", 
            estado_conservacion="Excelente", inauguracion=1811, categoria="Museo", 
            visible=True, registrado=datetime(2022, 10, 1), # <-- Fecha antigua
            ubicacion=WKTElement('Point(-68.5200 -31.5300)', srid=4326)
        ),
        Sitio(
            nombre="Bosques Petrificados (Viejo)", descripcion_breve="Yacimientos con árboles petrificados.", 
            descripcion_completa="...", ciudad="Jaramillo", provincia="Santa Cruz", 
            estado_conservacion="Bueno", inauguracion=2012, categoria="Natural", 
            visible=True, registrado=datetime(2022, 11, 15), # <-- Fecha antigua
            ubicacion=WKTElement('Point(-69.1706 -47.7811)', srid=4326)
        ),
        Sitio(
            nombre="Mausoleo de San Martín (Viejo)", descripcion_breve="Lugar de descanso final del Libertador.", 
            descripcion_completa="...", ciudad="Buenos Aires", provincia="Buenos Aires", 
            estado_conservacion="Excelente", inauguracion=1880, categoria="Monumento", 
            visible=True, registrado=datetime(2022, 12, 10), # <-- Fecha antigua
            ubicacion=WKTElement('Point(-58.3748 -34.6042)', srid=4326)
        ),
        Sitio(nombre="Monumento a la Bandera", descripcion_breve="Homenaje a la creación de la Bandera.", descripcion_completa="...", ciudad="Rosario", provincia="Santa Fe", estado_conservacion="Excelente", inauguracion=1957, categoria="Monumento", visible=True, ubicacion=WKTElement('Point(-60.6329 -32.9468)', srid=4326)),
        Sitio(nombre="Glaciar Perito Moreno", descripcion_breve="Impresionante glaciar en la Patagonia.", descripcion_completa="...", ciudad="El Calafate", provincia="Santa Cruz", estado_conservacion="Excelente", inauguracion=1937, categoria="Natural", visible=True, ubicacion=WKTElement('Point(-73.0463 -50.4859)', srid=4326)),
        Sitio(nombre="Obelisco de Buenos Aires", descripcion_breve="Símbolo de la capital argentina.", descripcion_completa="...", ciudad="Buenos Aires", provincia="Buenos Aires", estado_conservacion="Bueno", inauguracion=1936, categoria="Monumento", visible=True, ubicacion=WKTElement('Point(-58.3816 -34.6037)', srid=4326)),
        Sitio(nombre="Cueva de las Manos", descripcion_breve="Arte rupestre de 9.000 años.", descripcion_completa="...", ciudad="Perito Moreno", provincia="Santa Cruz", estado_conservacion="Regular", inauguracion=7300, categoria="Arqueológico", visible=True, ubicacion=WKTElement('Point(-70.6698 -47.1128)', srid=4326)),
        Sitio(nombre="Quebrada de Humahuaca", descripcion_breve="Paisajes de cerros multicolores.", descripcion_completa="...", ciudad="Purmamarca", provincia="Jujuy", estado_conservacion="Excelente", inauguracion=0, categoria="Natural", visible=True, ubicacion=WKTElement('Point(-65.3475 -23.2081)', srid=4326)),
        Sitio(nombre="Manzana Jesuítica", descripcion_breve="Bloque histórico en el centro de Córdoba.", descripcion_completa="...", ciudad="Córdoba", provincia="Córdoba", estado_conservacion="Excelente", inauguracion=1622, categoria="Religioso", visible=True, ubicacion=WKTElement('Point(-64.1883 -31.4206)', srid=4326)),
        Sitio(nombre="Pucará de Tilcara", descripcion_breve="Fortaleza prehispánica en Jujuy.", descripcion_completa="...", ciudad="Tilcara", provincia="Jujuy", estado_conservacion="Bueno", inauguracion=1000, categoria="Arqueológico", visible=True, ubicacion=WKTElement('Point(-65.3852 -23.5852)', srid=4326)),
        Sitio(nombre="Fuerte Barragán", descripcion_breve="Restos de una fortificación de defensa costera.", descripcion_completa="...", ciudad="Ensenada", provincia="Buenos Aires", estado_conservacion="Regular", inauguracion=1730, categoria="Militar", visible=True, ubicacion=WKTElement('Point(-57.9429 -34.8693)', srid=4326)),
        Sitio(nombre="Convento de San Francisco", descripcion_breve="Arquitectura barroca en Salta.", descripcion_completa="...", ciudad="Salta", provincia="Salta", estado_conservacion="Excelente", inauguracion=1759, categoria="Religioso", visible=True, ubicacion=WKTElement('Point(-65.4124 -24.7884)', srid=4326)),
        Sitio(nombre="Puente del Inca", descripcion_breve="Formación natural sobre el Río Mendoza.", descripcion_completa="...", ciudad="Puente del Inca", provincia="Mendoza", estado_conservacion="Regular", inauguracion=1800, categoria="Natural", visible=True, ubicacion=WKTElement('Point(-69.9079 -32.8258)', srid=4326)),
        Sitio(nombre="Museo Histórico de Cuyo", descripcion_breve="Colección sobre la historia de Mendoza.", descripcion_completa="...", ciudad="Mendoza", provincia="Mendoza", estado_conservacion="Bueno", inauguracion=1910, categoria="Museo", visible=True, ubicacion=WKTElement('Point(-68.8458 -32.8879)', srid=4326)),
        Sitio(nombre="Casa del Acuerdo", descripcion_breve="Lugar donde se firmó el Acuerdo de San Nicolás.", descripcion_completa="...", ciudad="San Nicolás de los Arroyos", provincia="Buenos Aires", estado_conservacion="Excelente", inauguracion=1852, categoria="Histórico", visible=True, ubicacion=WKTElement('Point(-60.2198 -33.3323)', srid=4326)),
        Sitio(nombre="Talampaya", descripcion_breve="Parque Nacional de cañones y paisajes únicos.", descripcion_completa="...", ciudad="Villa Unión", provincia="La Rioja", estado_conservacion="Bueno", inauguracion=1997, categoria="Natural", visible=True, ubicacion=WKTElement('Point(-67.8427 -30.0805)', srid=4326)),
        Sitio(nombre="Museo de la Casa Rosada", descripcion_breve="Colección presidencial y salones históricos.", descripcion_completa="...", ciudad="Buenos Aires", provincia="Buenos Aires", estado_conservacion="Excelente", inauguracion=1890, categoria="Museo", visible=True, ubicacion=WKTElement('Point(-58.3705 -34.6083)', srid=4326)),
        Sitio(nombre="Capilla de Candonga", descripcion_breve="Antigua capilla rural jesuítica de Córdoba.", descripcion_completa="...", ciudad="Candonga", provincia="Córdoba", estado_conservacion="Bueno", inauguracion=1730, categoria="Religioso", visible=True, ubicacion=WKTElement('Point(-64.3800 -31.0500)', srid=4326)),
        Sitio(nombre="Torre Monumental", descripcion_breve="Torre de los Ingleses, cerca del puerto.", descripcion_completa="...", ciudad="Buenos Aires", provincia="Buenos Aires", estado_conservacion="Regular", inauguracion=1916, categoria="Monumento", visible=True, ubicacion=WKTElement('Point(-58.3748 -34.5959)', srid=4326)),
        Sitio(nombre="Esteros del Iberá", descripcion_breve="Gran reserva de humedales en Corrientes.", descripcion_completa="...", ciudad="Colonia Carlos Pellegrini", provincia="Corrientes", estado_conservacion="Excelente", inauguracion=1982, categoria="Natural", visible=True, ubicacion=WKTElement('Point(-57.1738 -28.0933)', srid=4326)),
        Sitio(nombre="Faro de Ushuaia", descripcion_breve="El Faro del Fin del Mundo, en Tierra del Fuego.", descripcion_completa="...", ciudad="Ushuaia", provincia="Tierra del Fuego", estado_conservacion="Excelente", inauguracion=1884, categoria="Marítimo", visible=True, ubicacion=WKTElement('Point(-68.2750 -54.9450)', srid=4326)),
        Sitio(nombre="Castillo San Carlos", descripcion_breve="Ruinas de un fuerte militar en Entre Ríos.", descripcion_completa="...", ciudad="Concordia", provincia="Entre Ríos", estado_conservacion="Malo", inauguracion=1778, categoria="Militar", visible=True, ubicacion=WKTElement('Point(-58.0531 -31.3934)', srid=4326)),
        Sitio(nombre="Basílica de Luján", descripcion_breve="Principal templo mariano de Argentina.", descripcion_completa="...", ciudad="Luján", provincia="Buenos Aires", estado_conservacion="Excelente", inauguracion=1890, categoria="Religioso", visible=True, ubicacion=WKTElement('Point(-59.1062 -34.5668)', srid=4326)),
        Sitio(nombre="Valle de la Luna", descripcion_breve="Parque Provincial Ischigualasto, paisajes jurásicos.", descripcion_completa="...", ciudad="Valle Fértil", provincia="San Juan", estado_conservacion="Bueno", inauguracion=1971, categoria="Natural", visible=True, ubicacion=WKTElement('Point(-67.9511 -30.0638)', srid=4326)),
        Sitio(nombre="Dique San Roque", descripcion_breve="Antigua represa de ingeniería hidráulica.", descripcion_completa="...", ciudad="Villa Carlos Paz", provincia="Córdoba", estado_conservacion="Bueno", inauguracion=1890, categoria="Ingeniería", visible=True, ubicacion=WKTElement('Point(-64.4400 -31.3500)', srid=4326)),
        Sitio(nombre="Capilla Sagrado Corazón", descripcion_breve="Edificio gótico francés en La Plata.", descripcion_completa="...", ciudad="La Plata", provincia="Buenos Aires", estado_conservacion="Bueno", inauguracion=1903, categoria="Religioso", visible=True, ubicacion=WKTElement('Point(-57.9570 -34.9200)', srid=4326)),
        Sitio(nombre="Península Valdés", descripcion_breve="Reserva de fauna marina y ballenas.", descripcion_completa="...", ciudad="Puerto Madryn", provincia="Chubut", estado_conservacion="Excelente", inauguracion=1999, categoria="Natural", visible=True, ubicacion=WKTElement('Point(-64.2155 -42.4965)', srid=4326)),
        Sitio(nombre="Museo Ernesto Che Guevara", descripcion_breve="Casa natal del famoso revolucionario.", descripcion_completa="...", ciudad="Alta Gracia", provincia="Córdoba", estado_conservacion="Bueno", inauguracion=1928, categoria="Museo", visible=True, ubicacion=WKTElement('Point(-64.4264 -31.6559)', srid=4326)),
        Sitio(nombre="Ruinas de Epecuén", descripcion_breve="Pueblo abandonado inundado por el lago.", descripcion_completa="...", ciudad="Epecuén", provincia="Buenos Aires", estado_conservacion="Malo", inauguracion=1920, categoria="Ruinas", visible=True, ubicacion=WKTElement('Point(-62.8390 -37.1350)', srid=4326)),
        Sitio(nombre="Fuerte San Miguel", descripcion_breve="Antigua fortificación colonial en Corrientes.", descripcion_completa="...", ciudad="Ituzaingó", provincia="Corrientes", estado_conservacion="Regular", inauguracion=1780, categoria="Militar", visible=True, ubicacion=WKTElement('Point(-56.5800 -27.5700)', srid=4326)),
        Sitio(nombre="El Chaltén", descripcion_breve="Capital nacional del trekking, base del Fitz Roy.", descripcion_completa="...", ciudad="El Chaltén", provincia="Santa Cruz", estado_conservacion="Excelente", inauguracion=1985, categoria="Natural", visible=True, ubicacion=WKTElement('Point(-72.8800 -49.3300)', srid=4326)),
        Sitio(nombre="Túnel Subfluvial", descripcion_breve="Une las provincias de Santa Fe y Entre Ríos.", descripcion_completa="...", ciudad="Santa Fe", provincia="Santa Fe", estado_conservacion="Excelente", inauguracion=1969, categoria="Ingeniería", visible=True, ubicacion=WKTElement('Point(-60.6723 -31.6240)', srid=4326)),
        Sitio(nombre="Camino de las Estancias", descripcion_breve="Ruta de antiguas estancias jesuíticas en Córdoba.", descripcion_completa="...", ciudad="Jesús María", provincia="Córdoba", estado_conservacion="Bueno", inauguracion=1600, categoria="Cultural", visible=True, ubicacion=WKTElement('Point(-64.0800 -30.9800)', srid=4326)),
        Sitio(nombre="Basílica de Nuestra Señora del Pilar", descripcion_breve="Templo colonial de Buenos Aires.", descripcion_completa="...", ciudad="Buenos Aires", provincia="Buenos Aires", estado_conservacion="Excelente", inauguracion=1732, categoria="Religioso", visible=True, ubicacion=WKTElement('Point(-58.3800 -34.5800)', srid=4326)),
        Sitio(nombre="Museo Provincial de Ciencias", descripcion_breve="Dedicado a la paleontología y geología de Neuquén.", descripcion_completa="...", ciudad="Neuquén", provincia="Neuquén", estado_conservacion="Bueno", inauguracion=2000, categoria="Museo", visible=True, ubicacion=WKTElement('Point(-68.0500 -38.9500)', srid=4326)),
        Sitio(nombre="Cerro Uritorco", descripcion_breve="Montaña famosa por leyendas y avistamientos.", descripcion_completa="...", ciudad="Capilla del Monte", provincia="Córdoba", estado_conservacion="Bueno", inauguracion=0, categoria="Natural", visible=True, ubicacion=WKTElement('Point(-64.5772 -30.8583)', srid=4326)),
        Sitio(nombre="Iglesia de Uquía", descripcion_breve="Iglesia con pinturas de ángeles arcabuceros.", descripcion_completa="...", ciudad="Uquía", provincia="Jujuy", estado_conservacion="Bueno", inauguracion=1691, categoria="Religioso", visible=True, ubicacion=WKTElement('Point(-65.3400 -23.3600)', srid=4326)),
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
