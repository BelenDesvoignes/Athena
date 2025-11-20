# admin/src/routes/reviews.py
from flask import Blueprint, request, jsonify, session, redirect, url_for, flash
from src.core.database import db
from src.core.models.user import User
from src.core.review_service import list_reviews, get_review_by_id, approve_review, reject_review, delete_review
from src.web.handlers.auth import login_required, permission_required 

reviews_bp = Blueprint("reviews", __name__, url_prefix="/reviews")
from flask import render_template

@reviews_bp.route("", methods=["GET"])
@login_required
@permission_required("user_moderation")
def reviews_list():
    """
    Lista las reseñas filtradas y paginadas.

    Parámetros opcionales por querystring:
        - page (int): Número de página. Default=1.
        - per_page (int): Cantidad por página. Default=25.
        - status (str): Estado de la reseña (pending, approved, rejected).
        - site_id (int): ID del sitio.
        - rating_min (int): Calificación mínima.
        - rating_max (int): Calificación máxima.
        - date_from (date): Fecha mínima de creación.
        - date_to (date): Fecha máxima de creación.
        - user_search (str): Búsqueda por email/nombre de usuario.
        - site_name (str): Búsqueda por nombre del sitio.
        - sort_by (str): Campo por el cual ordenar. Default="created_at".
        - sort_dir (str): Dirección de orden ("asc" o "desc"). Default="desc".

    Retorna:
        - Renderiza la plantilla "reviews.html" con la paginación y los filtros aplicados.
    """
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 25))
    status = request.args.get("status")  
    site_id = request.args.get("site_id")
    rating_min = request.args.get("rating_min")
    rating_max = request.args.get("rating_max")
    date_from = request.args.get("date_from")  
    date_to = request.args.get("date_to")
    user_search = request.args.get("user_search")
    sort_by = request.args.get("sort_by", "created_at")
    sort_dir = request.args.get("sort_dir", "desc")
    site_name = request.args.get("site_name")


    pag = list_reviews(page=page, per_page=per_page, status=status, site_id=site_id,
                       rating_min=rating_min, rating_max=rating_max, date_from=date_from,
                       date_to=date_to, user_search=user_search, site_name=site_name, sort_by=sort_by, sort_dir=sort_dir)

    return render_template(
        "reviews.html",
        pagination=pag,
        request=request
    )


@reviews_bp.route("/<int:review_id>", methods=["GET"])
@login_required
@permission_required("user_moderation")
def review_detail(review_id):

    """
    Devuelve el detalle de una reseña en formato JSON.

    Parámetros:
        - review_id (int): ID de la reseña.

    Respuestas:
        - 200: JSON con los datos de la reseña.
        - 404: Si la reseña no existe.
    """
    review = get_review_by_id(review_id)
    if not review:
        return jsonify({"error": "no encontrado"}), 404
    return jsonify({
        "id": review.id,
        "site_id": review.site_id,
        "user_email": getattr(review.user, "email", None),
        "rating": review.rating,
        "content": review.content,
        "status": review.status.value,
        "rejection_reason": review.rejection_reason,
        "created_at": review.created_at.isoformat(),
    })

@reviews_bp.route("/<int:review_id>/approve", methods=["POST"])
@login_required
@permission_required("user_moderation")
def review_approve(review_id):
    """
    Marca una reseña como aprobada.

    Parámetros:
        - review_id (int): ID de la reseña a aprobar.

    Efectos:
        - Cambia el estado de la reseña a "approved".

    Redirección:
        - Siempre redirige a la lista de reseñas con mensaje flash.
    """
    try:
        review = approve_review(review_id, current_user())
       
        flash(f"Reseña ID {review_id} aprobada con éxito.", "success")
        return redirect(url_for('reviews.reviews_list'))
    except ValueError as e:
       
        flash(f"Error al aprobar la reseña ID {review_id}: {str(e)}", "danger")
        return redirect(url_for('reviews.reviews_list'))
@reviews_bp.route("/<int:review_id>/reject", methods=["POST"])
@login_required
@permission_required("user_moderation")
def review_reject(review_id):
    """
    Rechaza una reseña con una razón opcional.

    Parámetros JSON:
        - reason (str): Motivo del rechazo.

    Redirección:
        - Redirige a la lista con mensaje flash.
    """
    data = request.json or {}
    reason = data.get("reason", "")
    try:
        review = reject_review(review_id, reason, current_user())
        flash(f"Reseña ID {review_id} rechazada con éxito.", "success")
        return redirect(url_for('reviews.reviews_list'))
    except ValueError as e:
        flash(f"Error al rechazar la reseña ID {review_id}: {str(e)}", "danger")
        return redirect(url_for('reviews.reviews_list'))


@reviews_bp.route("/<int:review_id>", methods=["POST"])
@login_required
@permission_required("user_moderation")
def review_delete(review_id):
    """
    Elimina una reseña.

    Parámetros opcionales:
        - hard (bool): Si es true, borrado permanente. Default=False.

    Redirección:
        - Siempre vuelve a la lista con mensaje flash.
    """
    hard = request.args.get("hard", "false").lower() == "true"
    try:
        delete_review(review_id, hard_delete=hard)

        flash(f"Reseña ID {review_id} eliminada con éxito.", "success")
        return redirect(url_for('reviews.reviews_list'))
    except ValueError as e:

        flash(f"Error al eliminar la reseña ID {review_id}: {str(e)}", "danger")
        return redirect(url_for('reviews.reviews_list'))

def current_user():
    """
    Devuelve el usuario logueado basándose en la sesión.

    Retorna:
        - User: si existe.
        - None: si no hay usuario logueado.
    """
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)
