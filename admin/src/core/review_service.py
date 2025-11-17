# admin/src/core/review_service.py
from datetime import datetime, timezone
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload
from src.core.database import db
from src.core.models.user import User
from src.core.models.site import Sitio
from src.core.models.review import Review, ReviewStatus
from werkzeug.exceptions import NotFound
from datetime import datetime, timezone

def get_review_by_id(review_id):
    return db.session.query(Review).filter_by(id=review_id, deleted=False).first()

def list_reviews(page=1, per_page=25, status=None, site_id=None, rating_min=None, rating_max=None,
                 date_from=None, date_to=None, user_search=None, sort_by='created_at', sort_dir='desc'):

    query = db.session.query(Review).options(
        joinedload(Review.user),  # carga la relación User
        joinedload(Review.site)   # carga la relación Sitio
    ).filter_by(deleted=False)

    if status:
        query = query.filter(Review.status == ReviewStatus(status))
    if site_id:
        query = query.filter(Review.site_id == site_id)
    if rating_min is not None:
        query = query.filter(Review.rating >= int(rating_min))
    if rating_max is not None:
        query = query.filter(Review.rating <= int(rating_max))
    if date_from:
        query = query.filter(Review.created_at >= date_from)
    if date_to:
        query = query.filter(Review.created_at <= date_to)
    if user_search:
        query = query.join(User).filter(User.email.ilike(f"%{user_search}%"))

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
    review = get_review_by_id(review_id)
    if not review:
        raise NotFound(f"Reseña con ID {review_id} no encontrada.")
    review.status = ReviewStatus.APROBADA
    review.rejection_reason = None
    review.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return review

def reject_review(review_id, reason, moderator_user):
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
