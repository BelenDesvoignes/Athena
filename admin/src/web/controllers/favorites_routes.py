from flask import Blueprint, jsonify, g, abort, request, current_app
from src.core.database import db
from src.core.models.favorites import Favorite
from src.core.models.site import Sitio
from src.core.models.review import Review
from src.core.auth_decorators import login_required_public
from src.core.api_validations import validate_api_params, SiteListParams
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, and_, func, desc
from math import ceil

#  Importar la función de utilidad
from src.web.api.api import get_site_images

favorites_bp = Blueprint("favorites_api", __name__, url_prefix="/api/v1")
PER_PAGE = 25 # Constante definida por requerimiento

@favorites_bp.post("/sites/<int:sitio_id>/favorite")
@login_required_public
def add_favorite(sitio_id):
    """
    Marca un sitio como favorito para el usuario autenticado (g.public_user).
    """
    sitio = db.session.get(Sitio, sitio_id)
    if not sitio or not sitio.visible:
        return jsonify({"message": "Sitio no encontrado o no visible"}), 404

    user_id = g.public_user.id

    try:
        # Crea el nuevo registro de favorito
        new_favorite = Favorite(user_id=user_id, sitio_id=sitio_id)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({"message": "Sitio marcado como favorito"}), 201

    except IntegrityError:
        # Maneja el caso en que la clave única (user_id, sitio_id) ya existe
        db.session.rollback()
        return jsonify({"message": "El sitio ya es un favorito del usuario"}), 409
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al añadir favorito: {e}")
        return jsonify({"message": "Error interno del servidor"}), 500


@favorites_bp.delete("/sites/<int:sitio_id>/favorite")
@login_required_public
def remove_favorite(sitio_id):
    """
    Elimina un sitio de la lista de favoritos del usuario autenticado.
    """
    user_id = g.public_user.id

    # Buscar el registro de favorito específico
    favorite = db.session.scalar(
        select(Favorite).where(
            and_(Favorite.sitio_id == sitio_id, Favorite.user_id == user_id)
        )
    )

    if not favorite:
        return jsonify({"message": "El sitio no está marcado como favorito"}), 404

    try:
        # Eliminar el registro
        db.session.delete(favorite)
        db.session.commit()
        # Retorna 204 No Content para eliminación exitosa
        return "", 204
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al eliminar favorito: {e}")
        return jsonify({"message": "Error interno del servidor"}), 500


@favorites_bp.get("/user/favorites")
@login_required_public
@validate_api_params(SiteListParams)
def get_user_favorites(validated_params):
    """
    Lista los sitios marcados como favoritos por el usuario autenticado, con paginación.
    """
    user_id = g.public_user.id
    page = validated_params.page
    per_page = validated_params.per_page

    # Base query: Join Sitios con Favoritos y filtrar por user_id
    query_base = (
        db.session.query(Sitio)
        .join(Favorite, Sitio.id == Favorite.sitio_id)
        .filter(Favorite.user_id == user_id)
        .order_by(Favorite.id.desc())
    )

    #  Paginación
    total_items = query_base.count()
    pagination = query_base.paginate(page=page, per_page=per_page, error_out=False)

    data = []
    for sitio in pagination.items:

        #  obtener la calificación promedio
        promedio = (
            db.session.query(func.avg(Review.rating))
            .filter(Review.site_id == sitio.id, Review.status == "APROBADA")
            .scalar()
        )
        promedio = round(promedio, 2) if promedio else 0

        #  obtener la imagen de portada
        cover_url, _ = get_site_images(sitio)

        data.append({
            "id": sitio.id,
            "name": sitio.nombre,
            "short_description": sitio.descripcion_breve,
            "city": sitio.ciudad,
            "province": sitio.provincia,
            "state_of_conservation": sitio.estado_conservacion,
            "registered_date": sitio.registrado.strftime('%Y-%m-%d'),
            "average_rating": promedio, # 🚨 Agregado
            "tags": [{"id": t.id, "name": t.nombre} for t in sitio.tags[:5]],
            "image_url": cover_url, # 🚨 Agregado
            "is_favorite": True # Por definición, si está en esta lista es True
        })

    return jsonify({
        "data": data,
        "total": total_items,
        "pages": ceil(total_items / per_page),
        "page": page,
        "per_page": per_page
    })