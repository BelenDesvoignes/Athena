# admin/src/core/review_service.py
from datetime import datetime, timezone
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload
from src.core.database import db
from src.core.models.public_user import PublicUser
from src.core.models.site import Sitio
from src.core.models.review import Review, ReviewStatus
from werkzeug.exceptions import NotFound
from datetime import datetime, timezone

def get_review_by_id(review_id):
    """
    Obtiene una reseña por su ID solo si no está marcada como eliminada.

    Args:
        review_id (int): ID de la reseña.

    Returns:
        Review | None: La reseña encontrada o None si no existe.
    """
    return db.session.query(Review).filter_by(id=review_id, deleted=False).first()

def list_reviews(page=1, per_page=25, status=None, site_id=None, rating_min=None, rating_max=None,
                 date_from=None, date_to=None, user_search=None, site_name=None, sort_by='created_at', sort_dir='desc'):
    
    """
    Lista reseñas aplicando filtros, ordenamiento y paginación.

    Args:
        page (int): Número de página.
        per_page (int): Cantidad de resultados por página.
        status (str | None): Estado de la reseña (PENDIENTE, APROBADA, RECHAZADA).
        site_id (int | None): ID del sitio asociado.
        rating_min (int | None): Calificación mínima.
        rating_max (int | None): Calificación máxima.
        date_from (datetime | None): Fecha mínima de creación.
        date_to (datetime | None): Fecha máxima de creación.
        user_search (str | None): Filtro por email del usuario.
        site_name (str | None): Búsqueda parcial por nombre del sitio.
        sort_by (str): Campo de ordenamiento ('created_at' o 'rating').
        sort_dir (str): Dirección de ordenamiento ('asc' o 'desc').

    Returns:
        Pagination: Objeto con los resultados, páginas y metadatos.
    """

    query = db.session.query(Review).options(
        joinedload(Review.user),
        joinedload(Review.site)
    ).filter(Review.deleted == False)

   
    if site_name:
        query = query.join(Sitio)

    if status:
        query = query.filter(Review.status == ReviewStatus(status))
    if site_id:
        query = query.filter(Review.site_id == site_id)
    if site_name:
        query = query.filter(Sitio.nombre.ilike(f"%{site_name}%"))
    if rating_min: 
        try:
            query = query.filter(Review.rating >= int(rating_min))
        except ValueError:
            
            pass
    
    if rating_max:
        try:
            query = query.filter(Review.rating <= int(rating_max))
        except ValueError:
            
            pass
    if date_from:
        query = query.filter(Review.created_at >= date_from)
    if date_to:
        query = query.filter(Review.created_at <= date_to)
    if user_search:
        query = query.join(Review.user).filter(PublicUser.email.ilike(f"%{user_search}%"))

    if sort_by == 'created_at':
        order_col = Review.created_at
    elif sort_by == 'rating':
        order_col = Review.rating
    else:
        order_col = Review.created_at

    if sort_dir == 'asc':
        query = query.order_by(order_col.asc())
    else:
        query = query.order_by(order_col.desc())

    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    class Pagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page

    return Pagination(items, page, per_page, total)

def approve_review(review_id, moderator_user):
    """
    Aprueba una reseña y limpia el motivo de rechazo si lo tenía.

    Args:
        review_id (int): ID de la reseña.
        moderator_user (User): Usuario moderador que realiza la acción.

    Raises:
        NotFound: Si la reseña no existe.

    Returns:
        Review: La reseña actualizada.
    """
    review = get_review_by_id(review_id)
    if not review:
        raise NotFound(f"Reseña con ID {review_id} no encontrada.")
    review.status = ReviewStatus.APROBADA
    review.rejection_reason = None
    review.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return review

def reject_review(review_id, reason, moderator_user):
    """
    Rechaza una reseña asignando un motivo obligatorio.

    Args:
        review_id (int): ID de la reseña.
        reason (str): Motivo del rechazo.
        moderator_user (User): Usuario moderador.

    Raises:
        ValueError: Si el motivo no es válido o la reseña no existe.

    Returns:
        Review: Reseña actualizada con su estado y motivo.
    """
    if not reason or len(reason.strip()) == 0:
        raise ValueError("El motivo de rechazo es obligatorio.")
    if len(reason) > 200:
        raise ValueError("El motivo de rechazo no puede superar 200 caracteres.")
    review = get_review_by_id(review_id)
    if not review:
        raise ValueError("Reseña no encontrada.")
    review.status = ReviewStatus.RECHAZADA
    review.rejection_reason = reason.strip()
    review.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return review

def delete_review(review_id, hard_delete=False):
    """
    Elimina una reseña. Puede ser eliminación lógica o física.

    Args:
        review_id (int): ID de la reseña.
        hard_delete (bool): Si es True, se elimina definitivamente.

    Raises:
        ValueError: Si la reseña no existe.

    Returns:
        bool: True si se eliminó correctamente.
    """

    review = get_review_by_id(review_id)
    if not review:
        raise ValueError("Reseña no encontrada.")
    if hard_delete:
        db.session.delete(review)
    else:
        review.deleted = True
        review.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return True
