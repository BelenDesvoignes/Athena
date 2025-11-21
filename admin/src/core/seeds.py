from geoalchemy2.elements import WKTElement

from src.core.bcrypt import hash_password
from src.core.database import db
from src.core.models.feature_flags import FeatureFlag
from src.core.models.role_permission import Permission, Role, RolePermission
from src.core.models.site import Sitio
from src.core.models.user import User
from src.core.models.public_user import PublicUser
from src.core.models.tag import Tag
from src.core.models.review import Review, ReviewStatus
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError



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
        raise ValueError("No se encontró el rol Admin, corre seed_roles_permissions primero.")

    admin_role = db.session.query(Role).filter_by(name="Administrador").first()
    if not admin_role:
        raise ValueError("No se encontró el rol Administrador, corre seed_roles_permissions primero.")

    editor_role = db.session.query(Role).filter_by(name="Editor").first()
    if not editor_role:
        raise ValueError("No se encontró el rol Editor, corre seed_roles_permissions primero.")

    moderador_role = db.session.query(Role).filter_by(name="Moderador").first()
    if not moderador_role:
        raise ValueError("No se encontró el rol Moderador, corre seed_roles_permissions primero.")

    users_data = [
        {
            "nombre": "Admin",
            "apellido": "Principal",
            "email": "sysadmin@example.com",
            "password": hash_password("sysadmin123").decode("utf-8"),
            "role_id": admin_role.id,
            "system_admin": True,
        },
        {
            "nombre": "Administrador",
            "apellido": "Principal",
            "email": "admin@example.com",
            "password": hash_password("admin123").decode("utf-8"),
            "role_id": administrador_role.id,
            "system_admin": False,
        },
        {
            "nombre": "Editor",
            "apellido": "Principal",
            "email": "usuarioEditor@gmail.com",
            "password": hash_password("editor123").decode("utf-8"),
            "role_id": editor_role.id,
            "system_admin": False,
        },
        {
            "nombre": "Moderador",
            "apellido": "Principal",
            "email": "moderador@gmail.com",
            "password": hash_password("moderador123").decode("utf-8"),
            "role_id": moderador_role.id,
            "system_admin": False,
        },
    ]

    for data in users_data:
        existing = db.session.query(User).filter_by(email=data["email"]).first()
        if not existing:
            user = User(
                nombre=data["nombre"],
                apellido=data["apellido"],
                email=data["email"],
                password=data["password"],
                role_id=data["role_id"],
                system_admin=data["system_admin"],
                enabled=True,
                eliminado=False,
            )
            db.session.add(user)
            print(f"✅ Usuario creado: {data['email']}")
        else:
            print(f"⚠️ Usuario ya existe, omitido: {data['email']}")

    db.session.commit()
def slugify(text: str) -> str:
    """Convierte un texto en un slug válido."""
    return text.lower().replace(" ", "-")

def seed_tags():
    """Crea los tags iniciales si no existen."""
    tags_nombres = [
        "Histórico",
        "Cultura",
        "Museo",
        "Deporte",
        "Gastronomía",
        "Natural",
        "Arte",
        "Entretenimiento",
        "Educación"
    ]

    for nombre in tags_nombres:
        # Verifica si ya existe
        tag = db.session.query(Tag).filter_by(nombre=nombre).first()
        if not tag:
            slug = slugify(nombre)
            tag = Tag(
                nombre=nombre,
                slug=slug,
                fecha_creacion=datetime.now(timezone.utc)
            )
            db.session.add(tag)
    
    try:
        db.session.commit()
        print("Tags iniciales creados.")
    except IntegrityError as e:
        db.session.rollback()
        print(f"Error al crear tags: {e}")
def seed_sitios():

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

def asignar_tags_a_sitios():
    tags = {tag.nombre: tag for tag in db.session.query(Tag).all()}


    sitio = db.session.query(Sitio).filter_by(nombre="Ruinas de San Ignacio").first()
    if sitio:
        if tags["Histórico"] not in sitio.tags:
            sitio.tags.append(tags["Histórico"])
        if tags["Museo"] not in sitio.tags:
            sitio.tags.append(tags["Museo"])


    sitio = db.session.query(Sitio).filter_by(nombre="Quebrada de Humahuaca").first()
    if sitio and tags["Natural"] not in sitio.tags:
        sitio.tags.append(tags["Natural"])

    db.session.commit()
    print("Tags asignados a los sitios existentes.")

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
            "description": "Deshabilita temporalmente el portal web.",
            "is_enabled": False,
            "maintenance_message": None
        },
        {
            "key": "reviews_disabled",
            "display_name": "Deshabilitar nuevas reseñas",
            "description": "Deshabilita la creación y visualización de reseñas en el portal.",
            "is_enabled": False,
            "maintenance_message": None
        }
    ]

    for f in flags:
        exists = db.session.query(FeatureFlag).filter_by(key=f["key"]).first()
        if not exists:
            db.session.add(FeatureFlag(**f))

    db.session.commit()
    print("Feature flags iniciales creados.")


def seed_public_users():
    print("--- 3. Inicializando Usuarios Públicos (PublicUser) ---")
    
    public_users_data = [
        {"email": "user1@portal.com", "name": "Alice Tester"},
        {"email": "user2@portal.com", "name": "Bob Reviewer"},
        {"email": "user3@portal.com", "name": "Charlie Critic"},
    ]

    for data in public_users_data:
        existing = db.session.query(PublicUser).filter_by(email=data["email"]).first()
        if not existing:
            user = PublicUser(email=data["email"], name=data["name"])
            db.session.add(user)
            print(f"✅ PublicUser creado: {data['email']}")
        else:
            print(f"⚠️ PublicUser ya existe, omitido: {data['email']}")
    
    db.session.commit()


def seed_reviews():
    print("--- 5. Inicializando Reseñas (Reviews) ---")

    if db.session.query(Review).count() > 0:
        print("Reseñas ya existentes. Omitiendo siembra.")
        return

    # Obtener IDs de PublicUsers y Sitios
    user1 = db.session.query(PublicUser).filter_by(email="user1@portal.com").first()
    user2 = db.session.query(PublicUser).filter_by(email="user2@portal.com").first()
    user3 = db.session.query(PublicUser).filter_by(email="user3@portal.com").first()

    sitio1 = db.session.query(Sitio).filter_by(nombre="Cabildo de Buenos Aires").first()
    sitio2 = db.session.query(Sitio).filter_by(nombre="Ruinas de San Ignacio").first()
    sitio3 = db.session.query(Sitio).filter_by(nombre="Casa Histórica de Tucumán").first()
    sitio4 = db.session.query(Sitio).filter_by(nombre="Glaciar Perito Moreno").first()
    sitio5 = db.session.query(Sitio).filter_by(nombre="Manzana Jesuítica").first()
    
    
    if not all([user1, user2, user3, sitio1, sitio2, sitio3, sitio4, sitio5]):
        print("⚠️ No se pudieron encontrar todos los usuarios o sitios necesarios. Omitiendo siembra de reseñas.")
        return

    reviews_data = [
        
        Review(
            site_id=sitio1.id, user_id=user1.id, rating=5, 
            content="Una visita obligada para entender la historia argentina.",
            status=ReviewStatus.APROBADA,
            created_at=datetime(2023, 1, 10, tzinfo=timezone.utc)
        ),
        Review(
            site_id=sitio1.id, user_id=user2.id, rating=4, 
            content="Muy interesante, aunque la visita es un poco rápida.",
            status=ReviewStatus.PENDIENTE,
            created_at=datetime(2023, 1, 15, tzinfo=timezone.utc)
        ),
        # Reseña para Ruinas de San Ignacio (sitio2) - Pendiente
        Review(
            site_id=sitio2.id, user_id=user3.id, rating=5, 
            content="Las ruinas son impresionantes, el atardecer ahí es mágico.",
            status=ReviewStatus.PENDIENTE,
            created_at=datetime(2023, 2, 20, tzinfo=timezone.utc)
        ),
        # Reseña para Casa Histórica de Tucumán (sitio3) - Rechazada
        Review(
            site_id=sitio3.id, user_id=user1.id, rating=2, 
            content="Esperaba más del museo, la entrada es cara para lo que ofrece.",
            status=ReviewStatus.RECHAZADA,
            rejection_reason="Contenido inapropiado o irrelevante.",
            created_at=datetime(2023, 3, 5, tzinfo=timezone.utc)
        ),
        # Reseña para Glaciar Perito Moreno (sitio4)
        Review(
            site_id=sitio4.id, user_id=user2.id, rating=5, 
            content="¡La naturaleza en su máxima expresión! Increíble e inolvidable.",
            status=ReviewStatus.APROBADA,
            created_at=datetime(2023, 4, 1, tzinfo=timezone.utc)
        ),
        # Reseña para Manzana Jesuítica (sitio5)
        Review(
            site_id=sitio5.id, user_id=user3.id, rating=4, 
            content="Hermosa arquitectura, el recorrido histórico es muy completo.",
            status=ReviewStatus.PENDIENTE,
            created_at=datetime(2023, 4, 15, tzinfo=timezone.utc)
        ),
    ]

    db.session.add_all(reviews_data)
    db.session.commit()
    print(f"✅ Se han cargado {len(reviews_data)} reseñas de ejemplo.")




#if __name__ == "__main__":
#    with app.app_context():  # esto “activa” la app para poder usar db.session
#        seed_roles_permissions()
#        seed_sitios()
#        seed_admin_user()
