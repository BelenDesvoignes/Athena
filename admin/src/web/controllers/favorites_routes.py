from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.core.database import db
from src.core.models.favorites import Favorite
from src.core.models.site import Sitio
from src.core.models.review import Review
from src.core.models.images import Imagen
from sqlalchemy import func, and_, asc, desc
from geoalchemy2.functions import ST_Y, ST_X
from src.core.api_validations import validate_api_params, SiteListParams

from src.web.api.api import get_site_images


# Creamos el Blueprint para las rutas de favoritos.
favorites_bp = Blueprint("api_favorites", __name__, url_prefix="/api")


@favorites_bp.post("/sites/<int:site_id>/favorite")
@jwt_required()
def add_favorite(site_id):
    """
    Marca un sitio específico como favorito para el usuario autenticado.

    Requiere autenticación JWT. El ID del usuario se obtiene del token.
    Si el sitio no existe o no es visible, devuelve un error 404.
    Si ya es favorito, devuelve un estado 200 sin hacer cambios.

    Args:
        site_id (int): El ID del sitio a marcar como favorito, pasado en la URL.

    Returns:
        tuple: Una tupla que contiene el objeto JSON de respuesta y el código de estado HTTP.
               - 201 Created: Sitio marcado como favorito con éxito.
               - 200 OK: El sitio ya era favorito.
               - 404 Not Found: El sitio no existe o no es visible.
               - 500 Internal Server Error: Error en la base de datos al intentar guardar.
    """
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
    """
    Elimina un sitio específico de la lista de favoritos del usuario autenticado.

    Requiere autenticación JWT. El ID del usuario se obtiene del token.
    Si el sitio no existe en la lista de favoritos del usuario, la operación
    simplemente devuelve un éxito (200 OK) ya que el objetivo (eliminarlo) se cumple.

    Args:
        site_id (int): El ID del sitio a remover de la lista de favoritos, pasado en la URL.

    Returns:
        tuple: Una tupla que contiene el objeto JSON de respuesta y el código de estado HTTP.
               - 200 OK: Sitio eliminado de favoritos con éxito (o no estaba en la lista).
               - 500 Internal Server Error: Error en la base de datos al intentar eliminar.
    """
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


@favorites_bp.get("/me/favorites")
@favorites_bp.route("/me/favorites/", methods=["GET"])
@validate_api_params(SiteListParams)
@jwt_required()
def list_user_favorites(validated_params):
    """
    Lista paginada de sitios marcados como favoritos por el usuario autenticado.

    Esta función requiere autenticación JWT. Filtra los sitios para incluir solo
    aquellos que el usuario actual ha marcado como favoritos, aplicando paginación
    y opciones de ordenamiento.

    Args:
        validated_params (SiteListParams): Objeto que contiene los parámetros
            validados de la consulta (query parameters), incluyendo:
            - page (int): Número de la página a mostrar.
            - per_page (int): Cantidad de elementos por página.
            - order_by (str): Campo por el cual ordenar ('nombre', 'registrado', 'calificacion').
            - order (str): Dirección del ordenamiento ('asc' o 'desc').

    Returns:
        tuple: Una tupla que contiene el objeto JSON de respuesta y el código de estado HTTP (200 OK).
            El JSON incluye:
            - data (list): Lista de sitios serializados con información de promedio de rating y portada.
            - total (int): Número total de favoritos del usuario.
            - pages (int): Número total de páginas disponibles.
            - page (int): Página actual.
            - per_page (int): Elementos por página.
    """

    #  Autenticación y Parámetros
    user_id = get_jwt_identity()
    user_id_int = int(user_id)

    page = validated_params.page
    per_page = validated_params.per_page
    order_by = validated_params.order_by
    order_direction = validated_params.order

    #  Query Base con Promedio de Rating
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

    #  Favoritos del usuario
    query = query.join(
        Favorite, Sitio.id == Favorite.sitio_id
    ).filter(
        Favorite.user_id == user_id_int
    )

    #  Ordenamiento
    sort_column = None
    if order_by == "nombre":
        sort_column = Sitio.nombre
    elif order_by == "registrado":
        sort_column = Sitio.registrado
    elif order_by == "calificacion":
        sort_column = avg_rating

    if sort_column is not None:
        if order_direction == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(desc(Sitio.id))


    # Paginación y Serialización
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    data = []

    for row in pagination.items:
        sitio = row[0]
        promedio = row[1]

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
            "distance_km": None,
            # Se asume que tags se carga automáticamente por relación
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