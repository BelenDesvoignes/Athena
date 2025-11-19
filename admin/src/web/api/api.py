from sqlalchemy import func, or_, desc, asc, distinct, and_
from flask import Blueprint, jsonify, request, g, current_app
from src.core.models.review import Review
from src.core.database import db
from src.core.models.images import Imagen
from src.core.models.site import Sitio
from src.core.models.tag import Tag, sitios_tags
from src.core.api_validations import validate_api_params, SiteListParams
from geoalchemy2.functions import ST_X, ST_Y, ST_GeomFromText, ST_DistanceSphere
from minio import Minio
from datetime import timedelta
api_bp = Blueprint("api_public", __name__, url_prefix="/api")


def get_site_images(sitio, only_cover=False):
    """
    Obtiene imágenes del sitio y genera URLs presignadas.
    Si only_cover=True, solo devuelve la portada.
    Retorna (cover_url, cover_title, lista_de_imagenes)
    """

    minio_client = Minio(
        endpoint=current_app.config["MINIO_SERVER"],
        access_key=current_app.config["MINIO_ACCESS_KEY"],
        secret_key=current_app.config["MINIO_SECRET_KEY"],
        secure=current_app.config["MINIO_SECURE"]
    )
    bucket_name = current_app.config["MINIO_BUCKET"]

    default_url = "/img/default.jpg"

    if only_cover:
        portada = next((img for img in sitio.imagenes if img.es_portada), None)
        if portada:
            try:
                cover_url = minio_client.presigned_get_object(bucket_name, portada.ruta, expires=timedelta(hours=2))
            except:
                cover_url = default_url
            cover_title = portada.titulo
        else:
            cover_url = default_url
            cover_title = ""
        return cover_url, cover_title, []
    
    imagenes_data = []
    for img in sitio.imagenes:
        try:
            image_url = minio_client.presigned_get_object(bucket_name, img.ruta, expires=timedelta(hours=2))
        except:
            image_url = default_url

        imagenes_data.append({
            "id": img.id,
            "url": image_url,
            "title": img.titulo,
            "is_cover": img.es_portada
        })

    imagenes_data.sort(key=lambda x: not x["is_cover"])
    cover_url = imagenes_data[0]["url"] if imagenes_data else default_url
    cover_title = imagenes_data[0]["title"] if imagenes_data else ""

    return cover_url, cover_title, imagenes_data


@api_bp.get("/sites")
@api_bp.route("/sites/", methods=["GET"])
@validate_api_params(SiteListParams)
def get_sites(validated_params):

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

    # búsqueda
    if search_term:
        like = f"%{search_term}%"
        query = query.filter(or_(
            Sitio.nombre.ilike(like),
            Sitio.descripcion_breve.ilike(like)
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
        subquery = (
            db.session.query(sitios_tags.c.sitio_id)
            .filter(sitios_tags.c.tag_id.in_(tags_param))
            .group_by(sitios_tags.c.sitio_id)
            .having(func.count(sitios_tags.c.tag_id) == len(tags_param))
            .subquery()
        )
        query = query.filter(Sitio.id.in_(subquery))

    # distancia
    distance_km = None
    if lat is not None and lon is not None and radius_km:
        center = ST_GeomFromText(f'POINT({lon} {lat})', 4326)
        dist_meters = func.ST_DistanceSphere(Sitio.ubicacion, center)
        distance_km = (dist_meters / 1000.0).label("distance_km")
        query = query.filter(dist_meters <= radius_km * 1000)
        query = query.add_columns(distance_km)

    # ordenamiento
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
def get_site_detail(site_id):
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
        "images": imagenes_data
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

@api_bp.get("/flags/portal")
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

@api_bp.get("/flags/reviews")
def reviews_status():
    """
    Devuelve si las reseñas del portal están habilitadas o deshabilitadas.
    """
    reviews_enabled = g.feature_flags.get("reviews_enabled", True)

    return jsonify({
        "enabled": reviews_enabled,
        "flag": "reviews_enabled"
    }), 200