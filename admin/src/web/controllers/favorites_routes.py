from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.core.database import db
from src.core.models.favorites import Favorite
from src.core.models.site import Sitio

# Creamos el Blueprint para las rutas de favoritos.
favorites_bp = Blueprint("api_favorites", __name__, url_prefix="/api")


@favorites_bp.post("/sites/<int:site_id>/favorite")
@jwt_required()
def add_favorite(site_id):
    """Marca un sitio como favorito para el usuario autenticado."""
    # Nota: El token JWT contiene el 'public_users.id'
    user_id = int(get_jwt_identity())

    #  Verificar si el sitio existe y es visible
    sitio = db.session.query(Sitio).filter_by(id=site_id, visible=True).first()
    if not sitio:
        return jsonify({"msg": "Sitio no encontrado"}), 404

    #  Verificar si ya es favorito
    existing_fav = db.session.query(Favorite).filter_by(
        user_id=user_id,
        sitio_id=site_id
    ).first()

    if existing_fav:
        return jsonify({"msg": "El sitio ya está marcado como favorito"}), 200

    #  Crear favorito
    try:
        new_fav = Favorite(user_id=user_id, sitio_id=site_id)
        db.session.add(new_fav)
        db.session.commit()
        return jsonify({"msg": "Sitio marcado como favorito con éxito"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error al agregar favorito: {str(e)}"}), 500


@favorites_bp.delete("/sites/<int:site_id>/favorite")
@jwt_required()
def remove_favorite(site_id):
    """Elimina un sitio de la lista de favoritos del usuario autenticado."""
    user_id = int(get_jwt_identity())

    #  Buscar y eliminar el favorito
    try:
        rows_deleted = db.session.query(Favorite).filter_by(
            user_id=user_id,
            sitio_id=site_id
        ).delete()

        db.session.commit()

        if rows_deleted == 0:
            return jsonify({"msg": "El sitio no estaba marcado como favorito o no existe"}), 200

        return jsonify({"msg": "Sitio eliminado de favoritos con éxito"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error al eliminar favorito: {str(e)}"}), 500