from src.web.api.api import api_bp
from marshmallow import ValidationError
from src.core.database import db
from datetime import datetime, timezone
from src.core.models.site import Sitio
from src.core.models.public_user import PublicUser
from src.core.models.review import Review, ReviewStatus
from src.core.models.schema.Reviews import Review_Create_Schema
from src.web.handlers.maintenance import reviews_enabled_required
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from math import ceil

@api_bp.get("/sites/<int:site_id>/reviews")
@reviews_enabled_required
def get_site_reviews(site_id):
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    if page < 1 or per_page < 1 or per_page > 100:
        return jsonify({"error": "Parametros de paginacion invalidos"}), 400

    query = db.session.query(Review).filter_by(site_id=site_id, status=ReviewStatus.APROBADA)
    total_reviews = query.count()
    reviews = query.offset((page - 1) * per_page).limit(per_page).all()

    data = [
        {
            "id": review.id,
            "user_id": review.user_id,  
            "rating": review.rating,
            "comment": review.content,
            "status": review.status.value,
            "created_at": review.created_at.isoformat()
        }
        for review in reviews
    ]

    response = {
        "page": page,
        "per_page": per_page,
        "total": total_reviews,
        "total_pages": ceil(total_reviews / per_page),
        "reviews": data
    }
    return jsonify(response)


@api_bp.post("/sites/<int:site_id>/reviews", endpoint="create_site_review")
@jwt_required()
@reviews_enabled_required
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
        return jsonify({"error": "El ID del sitio en el cuerpo no coincide con la URL"}), 400

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

    return jsonify({
        "message": "Reseña creada exitosamente.",
        "review": {
            "id": new_review.id,
            "site_id": new_review.site_id,
            "user_id": new_review.user_id,
            "rating": new_review.rating,
            "comment": new_review.content,
            "status": new_review.status.value,
        }
    }), 201




@api_bp.put("/sites/<int:site_id>/reviews/<int:review_id>", endpoint="edite_site_review")
@jwt_required()
@reviews_enabled_required
def edite_site_review(site_id,review_id):
    review_schema = Review_Create_Schema()
    json_data = request.get_json()

    if not json_data:
        return jsonify({"error": "Debe enviar un cuerpo JSON"}), 400

    try:
        data = review_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    if data["site_id"] != site_id:
        return jsonify({"error": "El ID del sitio en el cuerpo no coincide con la URL"}), 400

    user_id = int(get_jwt_identity())
    review_editar = db.session.query(Review).filter_by(id=review_id,site_id=site_id).first()

    if review_editar.user_id != user_id:
        return jsonify({"error": "No tenés permiso para editar esta reseña"}), 403

    review_editar.rating = data["rating"]
    review_editar.content = data.get("comment", "")
    review_editar.status = ReviewStatus.PENDIENTE
    review_editar.updated_at = datetime.now(timezone.utc)
    
    db.session.commit()

    return jsonify({
        "message": "Reseña creada exitosamente.",
        "review": {
            "id": review_editar.id,
            "site_id": review_editar.site_id,
            "user_id": review_editar.user_id,
            "rating": review_editar.rating,
            "comment": review_editar.content,
            "status": review_editar.status.value,
        }
    }), 201


@api_bp.get("/sites/<int:site_id>/reviews/<int:review_id>", endpoint="get_site_review")
@jwt_required()
@reviews_enabled_required
def get_site_review(site_id, review_id):
    review = db.session.query(Review).filter_by(id=review_id, site_id=site_id).first()

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
@reviews_enabled_required
def delete_review(site_id, review_id):
    user_id = get_jwt_identity()
    user = db.session.query(PublicUser).filter_by(id=user_id).first()
    review = db.session.query(Review).filter_by(id=review_id, site_id=site_id).first()

    if not review:
        return jsonify({"msg": "Review no encontrada"}), 404

    if ((int(review.user_id) != int(user.id))):
        return jsonify({"msg": "No tenés permiso para eliminar esta reseña"}), 403

    db.session.delete(review)
    db.session.commit()

    return jsonify({"msg": "Review eliminada con éxito"}), 200


@api_bp.get("/flags/portal", endpoint="portal_status")
def portal_status():
    maintenance = g.feature_flags.get("portal_maintenance_mode", False)
    msg = g.feature_flags_msg.get("portal_maintenance_mode")

    return jsonify({
        "maintenance": maintenance,
        "message": msg or "El portal se encuentra en mantenimiento.",
        "flag": "portal_maintenance_mode"
    }), 209


@api_bp.get("/internal/users/<int:user_id>")
def get_user_info(user_id):
    print(f'Consulta recibida para el usuario con ID: {user_id}')
    user = db.session.query(PublicUser).filter_by(id=user_id).first()

    if not user:
        print(f'Usuario no encontrado para el ID: {user_id}')
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = {
        "nombre": user.name,
        "id": user.id,
    }

    print(f'Datos devueltos: {data}')
    return jsonify(data), 200


@api_bp.get("/sites/<int:site_id>/reviews/check", endpoint="check_site_review")
@jwt_required()
@reviews_enabled_required
def check_site_review(site_id):
    user_id = get_jwt_identity()
    review = db.session.query(Review).filter_by(site_id=site_id, user_id=user_id).first()

    if review:
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
        return jsonify({"has_reviewed": True, "review": review_data}), 200
    else:
        return jsonify({"has_reviewed": False}), 200


@api_bp.get("/me/reviews", endpoint="get_review_details")
@jwt_required()
@reviews_enabled_required
def get_review_details():
    user_id = get_jwt_identity()
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=25, type=int)
    if page < 1 or per_page < 1 or per_page > 100:
        return jsonify({"error": "Parametros de paginacion invalidos"}), 400

    query = (
        db.session.query(Review)
        .join(Sitio, Review.site_id == Sitio.id)
        .filter(Review.user_id == user_id)
    )
    total_reviews = query.count()
    reviews = query.offset((page - 1) * per_page).limit(per_page).all()


    
    data = [
        {
            "id": review.id,
            "site_id": review.site_id,
            "site_name": review.site.nombre,
            "user_id": review.user_id,  
            "rating": review.rating,
            "comment": review.content,
            "status": review.status.value,
            "created_at": review.created_at.isoformat()
        }
        for review in reviews
    ]

    response = {
    "page": page,
        "per_page": per_page,
        "total": total_reviews,
        "total_pages": ceil(total_reviews / per_page),
        "reviews": data
    }
    return jsonify(response),200
    
@api_bp.get("/flags/reviews")
def reviews_status():
    reviews_disabled = g.feature_flags.get("reviews_disabled", False)

    return jsonify({
        "disabled": reviews_disabled,
        "flag": "reviews_disabled"
    }), 200
