from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.core.user_service import list_users, create_user, update_user, delete_user, get_user_by_id
from src.web.handlers.auth import login_required, permission_required

user_bp = Blueprint("user", __name__, url_prefix="/admin/users", template_folder="../templates/admin/users")


@user_bp.route("/", methods=["GET"])
@login_required
@permission_required("user_index")
def index():
    page = request.args.get("page", 1, type=int)
    search_email = request.args.get("email")
    search_enabled = request.args.get("enabled")
    search_role_id = request.args.get("role_id")
    order_by = request.args.get("order_by", "fecha_creacion")
    order_dir = request.args.get("order_dir", "desc")

    pagination = list_users(
        page=page,
        per_page=25,
        search_email=search_email,
        search_enabled=search_enabled,
        search_role_id=search_role_id,
        order_by=order_by,
        order_dir=order_dir
    )
    users = pagination.items
    return render_template("index.html", users=users, pagination=pagination)


# Crear usuario
@user_bp.route("/new", methods=["GET", "POST"])
@login_required
@permission_required("user_new")
def new():
    if request.method == "POST":
        data = {
            "nombre": request.form.get("nombre"),
            "apellido": request.form.get("apellido"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
            "role_id": request.form.get("role_id"),
            "enabled": request.form.get("enabled") == "True"
        }
        try:
            create_user(data)
            flash("Usuario creado correctamente.", "success")
            return redirect(url_for("user.index"))
        except ValueError as e:
            flash(str(e), "danger")
    return render_template("form.html", user=None)


# Editar usuario
@user_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("user_update")
def edit(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("user.index"))

    if request.method == "POST":
        data = {
            "nombre": request.form.get("nombre"),
            "apellido": request.form.get("apellido"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
            "role_id": request.form.get("role_id"),
            "enabled": request.form.get("enabled") == "True"
        }
        try:
            update_user(user_id, data)
            flash("Usuario actualizado correctamente.", "success")
            return redirect(url_for("user.index"))
        except ValueError as e:
            flash(str(e), "danger")
    return render_template("form.html", user=user)


# Eliminar usuario
@user_bp.route("/<int:user_id>/delete", methods=["POST"])
@login_required
@permission_required("user_destroy")
def delete(user_id):
    try:
        delete_user(user_id)
        flash("Usuario eliminado correctamente.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("user.index"))
