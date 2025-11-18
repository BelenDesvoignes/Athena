from sqlalchemy import func
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import or_, func, desc, asc, distinct
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
)
from math import ceil
from src.core.database import db
from src.core.bcrypt import check_password
from src.core.models.site import Sitio
from src.core.models.tag import Tag
from src.core.models.user import User
from src.core.models.tag import sitios_tags
from src.core.models.review import Review, ReviewStatus
from src.core.models.schema.Reviews import Review_Schema, Review_Create_Schema


api_bp = Blueprint("api_public", __name__, url_prefix="/api")


# Endpoint de prueba para sitios
@api_bp.get("/sites")
def get_sites():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)  # 10 como default

    # calculo de calificacion promedio solo resenas aprobadas
    # coalesce(expr, 0) asegura que sitios sin reseñas tengan rating 0, no NULL.
    avg_rating = func.coalesce(
        func.avg(Review.rating).filter(Review.status == "APROBADA"), 0
    ).label("calificacion_promedio")

    # Query base: Selecciona el Sitio y el promedio calculado.
    query = db.session.query(Sitio, avg_rating).filter(Sitio.visible == True)

    # LEFT JOIN para incluir sitios que NO tienen reseñas
    # y luego agrupamos por Sitio para calcular el promedio por ID.
    query = query.outerjoin(
        Review, Sitio.id == Review.site_id).group_by(Sitio.id)

    # Manejo de Búsqueda por Texto (Aplica sobre nombre y descripción breve)
    search_term = request.args.get("search")
    if search_term:
        search_like = f"%{search_term}%"
        # Usa 'or_' para buscar el término en cualquiera de los dos campos
        query = query.filter(
            or_(
                Sitio.nombre.ilike(search_like),
                Sitio.descripcion_breve.ilike(search_like),
            )
        )

    #  Manejo de Filtros
    ciudad = request.args.get("city")
    provincia = request.args.get("province")
    estado = request.args.get("state")  # Estado de conservación

    if ciudad:
        query = query.filter(Sitio.ciudad.ilike(f"%{ciudad}%"))
    if provincia:
        query = query.filter(Sitio.provincia == provincia)
    if estado:
        query = query.filter(Sitio.estado_conservacion == estado)

    # Manejo de Tags (Filtro por multiselección)
    tags_param = request.args.get("tags")
    if tags_param:
        # Convierte los IDs de tags separados por coma a una lista de enteros
        tag_ids = [int(tid) for tid in tags_param.split(",") if tid.isdigit()]
        if tag_ids:
            # Hace un JOIN y filtra los sitios que contienen CUALQUIERA de los IDs
            query = query.join(Sitio.tags).filter(Tag.id.in_(tag_ids))

    #  Manejo de Ordenamiento
    # 'registrado' por defecto, para cumplir el requisito de 'fecha de registro'
    order_by = request.args.get("order_by", "registrado")
    order_direction = request.args.get("order", "desc")

    if order_by == "nombre":
        sort_column = Sitio.nombre
    elif order_by == "registrado":
        sort_column = Sitio.registrado
    elif order_by == "calificacion":
        sort_column = avg_rating

    # Aplicar la dirección del orden
    if sort_column is not None:
        if order_direction == "asc":
            query = query.order_by(asc(sort_column))
        else:  # 'desc' o cualquier otro valor por defecto
            query = query.order_by(desc(sort_column))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    data = []
    for sitio, promedio_rating in pagination.items:
        data.append(
            {
                "id": sitio.id,
                "name": sitio.nombre,
                "short_description": sitio.descripcion_breve,
                "city": sitio.ciudad,
                "province": sitio.provincia,
                "state_of_conservation": sitio.estado_conservacion,
                "registered_date": sitio.registrado.strftime("%Y-%m-%d"),
                "average_rating": round(promedio_rating, 2),
                # Incluir tags asociados (mostrar 5 máximo, como pide la consigna)
                "tags": [{"id": t.id, "name": t.nombre} for t in sitio.tags[:5]],
                # URL de imagen de portada (placeholder)
                "image_url": "/img/default.jpg",
            }
        )

    return jsonify(
        {
            "data": data,
            "total": pagination.total,
            "pages": pagination.pages,
            "page": pagination.page,
            "per_page": pagination.per_page,
        }
    )


# endpoint para obtener provincias unicas (GET /api/provinces)
@api_bp.get("/provinces")
def get_provinces():
    # Consulta a la DB para obtener una lista de todas las provincias
    # únicas donde hay sitios visibles
    provinces = (
        db.session.query(distinct(Sitio.provincia))
        .filter(Sitio.visible == True)
        .order_by(Sitio.provincia)
        .all()
    )
    # Formatea la respuesta como una lista simple de strings
    data = [p[0] for p in provinces]

    return jsonify(data)


# endpoint para obtener todos los Tags (GET /api/tags)
@api_bp.get("/tags")
def get_all_tags():
    # Consulta a la DB para obtener todos los tags
    tags = db.session.query(Tag).order_by(Tag.nombre).all()

    # Formatea a la estructura {id, name}
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