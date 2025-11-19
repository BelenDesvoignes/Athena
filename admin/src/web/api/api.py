from sqlalchemy import func, or_, desc, asc, distinct, and_
from flask import Blueprint, jsonify, request, g, current_app
from src.core.models.review import Review
from src.core.database import db
from src.core.models.images import Imagen
from src.core.bcrypt import check_password
from src.core.models.site import Sitio
from src.core.models.tag import Tag, sitios_tags
from src.core.api_validations import validate_api_params, SiteListParams
from geoalchemy2.functions import ST_X, ST_Y, ST_GeomFromText, ST_DistanceSphere
from minio import Minio
from datetime import timedelta
from src.core.models.tag import Tag
from src.core.models.user import User
from src.core.models.tag import sitios_tags
from src.core.models.review import Review, ReviewStatus
from src.core.models.schema.Reviews import Review_Schema, Review_Create_Schema


api_bp = Blueprint("api_public", __name__, url_prefix="/api")


def get_site_images(sitio):
    """
    Obtiene todas las imágenes del sitio, genera URLs presignadas
    y retorna (portada_url, lista_de_imagenes).
    """

    minio_client = Minio(
        endpoint=current_app.config["MINIO_SERVER"],
        access_key=current_app.config["MINIO_ACCESS_KEY"],
        secret_key=current_app.config["MINIO_SECRET_KEY"],
        secure=current_app.config["MINIO_SECURE"]
    )
    bucket_name = current_app.config["MINIO_BUCKET"]

    default_url = "/img/default.jpg"
    imagenes_data = []

    for img in sitio.imagenes:
        image_url = default_url

        try:
            image_url = minio_client.presigned_get_object(
                bucket_name,
                img.ruta,
                expires=timedelta(hours=2)
            )
        except:
            pass

        imagenes_data.append({
            "id": img.id,
            "url": image_url,
            "is_cover": img.es_portada
        })

    imagenes_data.sort(key=lambda x: not x["is_cover"])

    cover_url = imagenes_data[0]["url"] if imagenes_data else default_url

    return cover_url, imagenes_data


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

        cover_url, _ = get_site_images(sitio)

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
            "image_url": cover_url
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

    cover_url, imagenes_data = get_site_images(sitio)

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
        "cover_image": cover_url,
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


"""Api para identificarse en jwt"""


@api_bp.post("/auth", endpoint="login")
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    query = db.session.query(User).filter(User.email == email)
    user = query.first()
    if not user or not check_password(password, user.password):
        return jsonify({"msg": "Usuario o contraseña incorrectos"}), 401
    
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": access_token,
        "expires_in": 3600
    }), 200


"""Api para cerrar sesion en jwt"""
"""Se crea un token con la id del usuario y se envia en una cookie segura"""

@api_bp.post("/logout", endpoint="logout")
def logout():
    return jsonify({"msg": "Logout exitoso"}), 200


"""API para obtener reviews de un sitio específico"""


@api_bp.get("/sites/<int:site_id>/reviews")
def get_site_reviews(site_id):
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    """Validacion de parametros"""
    if page < 1 or per_page < 1 or per_page > 100:
        return jsonify({"error": "Parametros de paginacion invalidos"}), 400
    query = db.session.query(Review).filter_by(site_id=site_id)
    total_reviews = query.count()
    reviews = query.offset((page - 1) * per_page).limit(per_page).all()
    data = [
        {
            "id": review.id,
            "user_id": review.user_id,
            "rating": review.rating,
            "comment": review.content,
            "created_at": review.created_at.isoformat(),
        }
        for review in reviews
    ]
    response = {
        "page": page,
        "per_page": per_page,
        "total": total_reviews,
        "tatal_pages": ceil(total_reviews / per_page),
        "reviews": data,
    }
    return jsonify(response)


"""Metodo para crear una nueva review para un sitio turistico"""


@api_bp.post("/sites/<int:site_id>/reviews", endpoint="create_site_review")
@jwt_required()
def create_site_review(site_id):
    review_schema = Review_Create_Schema()
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "Debe enviar un cuerpo JSON"}), 400
    try:
        data = review_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    if data["site_id"] != site_id:
        return (
            jsonify(
                {"error": "El ID del sitio en el cuerpo no coincide con la URL"}),
            400,
        )
    user_id = int(get_jwt_identity())
    new_review = Review(
        site_id=site_id,
        user_id=user_id,
        rating=data["rating"],
        content=data.get("comment", ""),
        status=ReviewStatus.PENDIENTE,
    )
    db.session.add(new_review)
    db.session.commit()
    return (
        jsonify(
            {
                "message": "Reseña creada exitosamente.",
                "review": {
                    "id": new_review.id,
                    "site_id": new_review.site_id,
                    "user_id": new_review.user_id,
                    "rating": new_review.rating,
                    "comment": new_review.content,
                    "status": new_review.status.value,
                },
            }
        ),
        201,
    )


@api_bp.get("/sites/<int:site_id>/reviews/<int:review_id>", endpoint="get_site_review")
@jwt_required()
def get_site_review(site_id, review_id):
    review = db.session.query(Review).filter_by(
        id=review_id, site_id=site_id).first()
    if not review:
        return jsonify({"error": "Reseña no encontrada"}), 404
    review_data = {
        "id": review.id,
        "site_id": review.site_id,
        "user_id": review.user_id,
        "rating": review.rating,
        "comment": review.content,
        "status": review.status.value,
        "created_at": review.created_at.isoformat(),
        "updated_at": review.updated_at.isoformat(),
    }
    return jsonify(review_data)


@api_bp.delete("/sites/<int:site_id>/reviews/<int:review_id>", endpoint="delete_site_review")
@jwt_required()
def delete_review(site_id, review_id):
    user_id = get_jwt_identity()  

    
    review = db.session.query(Review).filter_by(
        id=review_id, site_id=site_id).first()

    if not review:
        return jsonify({"msg": "Review no encontrada"}), 404

    if int(review.user_id) != int(user_id):
        return jsonify({"msg": "No tenés permiso para eliminar esta reseña"}), 403

    db.session.delete(review)
    db.session.commit()

    return jsonify({"msg": "Review eliminada con éxito"}), 200
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