from sqlalchemy import func, or_, desc, asc, distinct
from flask import Blueprint, jsonify, request, g
from src.core.models.review import Review
from src.core.database import db
from src.core.models.site import Sitio
from src.core.models.tag import Tag, sitios_tags
from src.core.api_validations import validate_api_params, SiteListParams
from geoalchemy2.functions import ST_X, ST_Y, ST_GeomFromText, ST_DistanceSphere

api_bp = Blueprint("api_public", __name__, url_prefix="/api")

@api_bp.get("/sites")
@api_bp.route("/sites/", methods=["GET"])
@validate_api_params(SiteListParams)
def get_sites(validated_params):

    # parámetros validados
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

    # calificación promedio solo reseñas aprobadas
    avg_rating = func.coalesce(
        func.avg(Review.rating).filter(Review.status == 'APROBADA'),
        0
    ).label('calificacion_promedio')

    # Query base
    query = db.session.query(Sitio, avg_rating).filter(Sitio.visible == True)
    query = query.outerjoin(Review, Sitio.id == Review.site_id).group_by(Sitio.id)

    # búsqueda por texto
    if search_term:
        search_like = f"%{search_term}%"
        query = query.filter(or_(
            Sitio.nombre.ilike(search_like),
            Sitio.descripcion_breve.ilike(search_like)
        ))

    # filtros
    if ciudad:
        query = query.filter(Sitio.ciudad.ilike(f"%{ciudad}%"))
    if provincia:
        query = query.filter(Sitio.provincia == provincia)
    if estado:
        query = query.filter(Sitio.estado_conservacion == estado)

    # tags
    if tags_param:
        subquery = db.session.query(sitios_tags.c.sitio_id).filter(
            sitios_tags.c.tag_id.in_(tags_param)
        ).group_by(sitios_tags.c.sitio_id).having(
            func.count(sitios_tags.c.tag_id) == len(tags_param)
        ).subquery()
        query = query.filter(Sitio.id.in_(subquery))

    # filtrado por proximidad
    distance_km = None
    if lat is not None and lon is not None and radius_km is not None and radius_km > 0:
        center_point = ST_GeomFromText(f'POINT({lon} {lat})', 4326)
        distance_meters = func.ST_DistanceSphere(Sitio.ubicacion, center_point)
        distance_km = (distance_meters / 1000.0).label('distance_km')
        query = query.filter(distance_meters <= radius_km * 1000)
        query = query.add_columns(distance_km)

    # ORDENAMIENTO CORREGIDO
    sort_column = None
    column_names = [c.get('name') for c in query.column_descriptions]

    if order_by == 'nombre':
        sort_column = Sitio.nombre
    elif order_by == 'registrado':
        sort_column = Sitio.registrado
    elif order_by == 'calificacion':
        sort_column = avg_rating
    elif order_by == 'distancia' and 'distance_km' in column_names:
        sort_column = db.column('distance_km')

    if sort_column is not None:
        if order_direction == 'asc':
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

    # paginación
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # construir data de respuesta
    data = []
    for row in pagination.items:
        sitio = row[0]
        promedio_rating = row[1]
        distance_val = row[2] if len(row) > 2 else None

        data.append({
            "id": sitio.id,
            "name": sitio.nombre,
            "short_description": sitio.descripcion_breve,
            "city": sitio.ciudad,
            "province": sitio.provincia,
            "state_of_conservation": sitio.estado_conservacion,
            "registered_date": sitio.registrado.strftime('%Y-%m-%d'),
            "average_rating": round(promedio_rating, 2),
            "latitude": db.session.scalar(ST_Y(sitio.ubicacion)),
            "longitude": db.session.scalar(ST_X(sitio.ubicacion)),
            "distance_km": round(distance_val, 2) if distance_val is not None else None,
            "tags": [{"id": t.id, "name": t.nombre} for t in sitio.tags[:5]],
            "image_url": "/img/default.jpg",
        })

    return jsonify({
        "data": data,
        "total": pagination.total,
        "pages": pagination.pages,
        "page": pagination.page,
        "per_page": pagination.per_page,
    })


@api_bp.get("/sites/<int:site_id>")
def get_site_detail(site_id):
    sitio = db.session.query(Sitio).filter_by(id=site_id, visible=True).first()
    if not sitio:
        return jsonify({"error": "Sitio no encontrado"}), 404

    promedio = (
        db.session.query(func.avg(Review.rating))
        .filter(Review.site_id == sitio.id, Review.status == 'APROBADA')
        .scalar()
    )
    promedio = round(promedio, 2) if promedio else 0

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
        "image_url": "/img/default.jpg",
    }

    return jsonify(data)


@api_bp.get("/provinces")
def get_provinces():
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
    tags = db.session.query(Tag).order_by(Tag.nombre).all()
    data = [{"id": t.id, "name": t.nombre} for t in tags]
    return jsonify(data)

@api_bp.get("/flags")
def portal_status():
    """
    Devuelve el estado del portal (mantenimiento o activo).
    """
    maintenance = g.feature_flags.get("portal_maintenance_mode", False)
    msg = g.feature_flags_msg.get("portal_maintenance_mode")

    return jsonify({
        "maintenance": maintenance,
        "message": msg or "El portal se encuentra en mantenimiento.",
        "flag": "portal_maintenance_mode"
    }), 209