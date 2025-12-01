from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.core.database import db
from src.core.models.site import Sitio
from src.core.models.review import Review
from src.core.models.favorites import Favorite
from sqlalchemy import func, desc, asc
from geoalchemy2.functions import ST_GeomFromText, ST_X, ST_Y
from .minio import get_site_images
from src.core.api_validations import validate_api_params, SiteListParams
from src.web.api.api import api_bp
from src.core.models.tag import Tag, sitios_tags
from sqlalchemy import func, or_, desc, asc, distinct, and_
from src.core.models.images import Imagen


@api_bp.get("/sites")
@api_bp.route("/sites/", methods=["GET"])
@validate_api_params(SiteListParams)
@jwt_required(optional=True)
def get_sites(validated_params):
    """
    Recupera una lista paginada y filtrada de sitios turísticos visibles.

    Este endpoint soporta múltiples criterios de filtrado (búsqueda por texto, ubicación, tags)
    y permite la autenticación opcional. Si se solicita filtrar por favoritos ('is_favorite=true'),
    la autenticación se vuelve requerida.

    Args:
        validated_params (SiteListParams): Objeto que contiene los parámetros
            validados de la consulta (query parameters), incluyendo:
            - page (int): Número de página.
            - per_page (int): Elementos por página.
            - order_by (str): Campo de ordenamiento ('nombre', 'registrado', 'calificacion', 'distancia').
            - order (str): Dirección del ordenamiento ('asc' o 'desc').
            - search (str, optional): Término de búsqueda en nombre o descripción.
            - city (str, optional): Filtro por ciudad.
            - province (str, optional): Filtro por provincia.
            - state (str, optional): Filtro por estado de conservación.
            - tags (list[int], optional): Lista de IDs de tags (AND lógico).
            - lat (float, optional): Latitud del centro de búsqueda.
            - lon (float, optional): Longitud del centro de búsqueda.
            - radius_km (int, optional): Radio de búsqueda en kilómetros (requiere lat/lon).
            - is_favorite (bool, optional): Si es True, filtra solo los favoritos del usuario autenticado.

    Returns:
        tuple: Una tupla que contiene el objeto JSON de respuesta y el código de estado HTTP.
               - 200 OK: Lista de sitios paginada.
               - 401 Unauthorized: Si se solicita 'is_favorite=true' sin autenticación JWT.

            El JSON devuelto incluye:
            - data (list): Lista de objetos Sitio con promedio de rating, imagen de portada, y distancia (si se usó geolocalización).
            - total (int): Total de sitios que coinciden con los filtros.
            - pages (int): Total de páginas disponibles.
    """

    page = validated_params.page
    per_page = validated_params.per_page
    order_by = validated_params.order_by
    order_direction = validated_params.order
    search_term = validated_params.search
    ciudad = validated_params.city
    provincia = validated_params.province
    estado = validated_params.state
    tags_param = validated_params.tags
    lat = validated_params.lat
    lon = validated_params.lon
    radius_km = validated_params.radius
    is_favorite = validated_params.is_favorite

    user_id = get_jwt_identity()
    user_id_int = None

    if is_favorite and user_id is None:
        # Si pide filtrar favoritos pero NO hay identidad de usuario (token ausente o inválido)
        return jsonify({"error": "Se requiere autenticación para acceder a los sitios favoritos."}), 401

    if user_id is not None:
        try:
            user_id_int = int(user_id)
        except ValueError:
            user_id_int = None

    avg_rating = func.coalesce(
        func.avg(Review.rating).filter(Review.status == 'APROBADA'),
        0
    ).label('calificacion_promedio')

    query = (
        db.session.query(Sitio, avg_rating, Imagen)
        .outerjoin(Review, Sitio.id == Review.site_id)
        .outerjoin(Imagen, and_(Imagen.sitio_id == Sitio.id, Imagen.es_portada == True))
        .filter(Sitio.visible == True)
        .group_by(Sitio.id, Imagen.id)
    )

    if search_term:
        like = f"%{search_term}%"
        query = query.filter(or_(
            Sitio.nombre.ilike(like),
            Sitio.descripcion_breve.ilike(like)
        ))

    if ciudad:
        query = query.filter(Sitio.ciudad.ilike(f"%{ciudad}%"))
    if provincia:
        query = query.filter(Sitio.provincia == provincia)
    if estado:
        query = query.filter(Sitio.estado_conservacion == estado)

    if tags_param:
        subquery = (
            db.session.query(sitios_tags.c.sitio_id)
            .filter(sitios_tags.c.tag_id.in_(tags_param))
            .group_by(sitios_tags.c.sitio_id)
            .having(func.count(sitios_tags.c.tag_id) == len(tags_param))
            .subquery()
        )
        query = query.filter(Sitio.id.in_(subquery))

    if is_favorite and user_id_int is not None:
        query = query.join(
            Favorite, Sitio.id == Favorite.sitio_id
        ).filter(
            Favorite.user_id == user_id_int
        )

    distance_km = None
    if lat is not None and lon is not None and radius_km:
        center = ST_GeomFromText(f'POINT({lon} {lat})', 4326)
        dist_meters = func.ST_DistanceSphere(Sitio.ubicacion, center)
        distance_km = (dist_meters / 1000.0).label("distance_km")
        query = query.filter(dist_meters <= radius_km * 1000)
        query = query.add_columns(distance_km)

    column_names = [c.get('name') for c in query.column_descriptions]
    sort_column = None

    if order_by == "nombre":
        sort_column = Sitio.nombre
    elif order_by == "registrado":
        sort_column = Sitio.registrado
    elif order_by == "calificacion":
        sort_column = avg_rating
    elif order_by == "distancia" and "distance_km" in column_names:
        sort_column = db.column("distance_km")

    if sort_column is not None:
        if order_direction == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    data = []

    for row in pagination.items:
        sitio = row[0]
        promedio = row[1]
        distancia_val = row[3] if len(row) > 3 else None

        cover_url, cover_title, _ = get_site_images(sitio, only_cover=True)

        data.append({
            "id": sitio.id,
            "name": sitio.nombre,
            "short_description": sitio.descripcion_breve,
            "city": sitio.ciudad,
            "province": sitio.provincia,
            "state_of_conservation": sitio.estado_conservacion,
            "registered_date": sitio.registrado.strftime('%Y-%m-%d'),
            "average_rating": round(promedio, 2),
            "latitude": db.session.scalar(ST_Y(sitio.ubicacion)),
            "longitude": db.session.scalar(ST_X(sitio.ubicacion)),
            "distance_km": round(distancia_val, 2) if distancia_val else None,
            "tags": [{"id": t.id, "name": t.nombre} for t in sitio.tags[:5]],
            "image_url": cover_url,
            "image_title": cover_title
        })

    return jsonify({
        "data": data,
        "total": pagination.total,
        "pages": pagination.pages,
        "page": pagination.page,
        "per_page": pagination.per_page
    })


@api_bp.get("/sites/<int:site_id>")
@jwt_required(optional=True)
def get_site_detail(site_id):
    """
    Obtiene los detalles completos de un sitio turístico específico.

    Incluye información general, promedio de rating de las reviews aprobadas,
    y verifica si el sitio está marcado como favorito por el usuario actual (si está autenticado).

    Args:
        site_id (int): El ID del sitio cuyos detalles se desean obtener, pasado en la URL.

    Requires:
        @jwt_required(optional=True): La autenticación JWT es opcional.

    Returns:
        tuple: Una tupla que contiene el objeto JSON de respuesta y el código de estado HTTP.
               - 200 OK: Retorna los datos detallados del sitio.
               - 404 Not Found: Si el sitio no existe o no está marcado como visible.

            El JSON devuelto incluye campos detallados como:
            - id, name, description, city, province, state_of_conservation, etc.
            - average_rating (float): Promedio de calificación basado en reviews aprobadas.
            - latitude (float) y longitude (float): Coordenadas geográficas.
            - tags (list): Lista de tags asociados al sitio.
            - cover_image (dict): URL y título de la imagen de portada.
            - images (list): Lista de todas las imágenes del sitio.
            - is_favorite (bool): Indica si el usuario autenticado tiene el sitio como favorito.
    """

    sitio = db.session.query(Sitio).filter_by(id=site_id, visible=True).first()
    if not sitio:
        return jsonify({"error": "Sitio no encontrado"}), 404

    promedio = (
        db.session.query(func.avg(Review.rating))
        .filter(Review.site_id == sitio.id, Review.status == "APROBADA")
        .scalar()
    )
    promedio = round(promedio, 2) if promedio else 0

    cover_url, cover_title, imagenes_data = get_site_images(sitio)

    is_favorite_for_user = False
    user_id = get_jwt_identity()

    if user_id:
        user_id_int = int(user_id)
        existing_fav = db.session.query(Favorite).filter_by(
            user_id=user_id_int,
            sitio_id=sitio.id
        ).first()
        if existing_fav:
            is_favorite_for_user = True

    data = {
        "id": sitio.id,
        "name": sitio.nombre,
        "description": sitio.descripcion_completa,
        "short_description": sitio.descripcion_breve,
        "city": sitio.ciudad,
        "province": sitio.provincia,
        "state_of_conservation": sitio.estado_conservacion,
        "registered_date": sitio.registrado.strftime('%Y-%m-%d'),
        "average_rating": promedio,
        "latitude": db.session.scalar(ST_Y(sitio.ubicacion)),
        "longitude": db.session.scalar(ST_X(sitio.ubicacion)),
        "tags": [{"id": t.id, "name": t.nombre} for t in sitio.tags],
        "cover_image": {
            "url": cover_url,
            "title": cover_title
        },
        "images": imagenes_data,
        "is_favorite": is_favorite_for_user
    }

    return jsonify(data)


@api_bp.get("/provinces")
def get_provinces():
    """
    Obtiene una lista única y ordenada alfabéticamente de todas las provincias
    asociadas a sitios turísticos visibles.

    Este endpoint se utiliza generalmente para poblar filtros en la interfaz de usuario.

    Returns:
        tuple: Una tupla que contiene el objeto JSON de respuesta y el código de estado HTTP (200 OK).
               El JSON devuelto es una lista simple de strings.
    """
    provinces = (
        db.session.query(distinct(Sitio.provincia))
        .filter(Sitio.visible == True)
        .order_by(Sitio.provincia)
        .all()
    )
    data = [p[0] for p in provinces]
    return jsonify(data)


@api_bp.get("/tags")
def get_all_tags():
    """
    Obtiene la lista completa de todos los tags disponibles en el sistema.

    La lista de tags se ordena alfabéticamente por nombre y se devuelve
    en un formato de ID y nombre, útil para poblar filtros o selectores.

    Returns:
        tuple: Una tupla que contiene el objeto JSON de respuesta y el código de estado HTTP (200 OK).
               El JSON devuelto es una lista de diccionarios.
    """
    tags = db.session.query(Tag).order_by(Tag.nombre).all()
    data = [{"id": t.id, "name": t.nombre} for t in tags]
    return jsonify(data)