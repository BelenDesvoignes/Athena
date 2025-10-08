from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.core.tag_service import generate_slug, get_tag_by_slug, create_tag, list_tags, delete_tag, update_tag, get_tag_by_name, used_tag
from src.core.models import Tag
from src.web.handlers.auth import login_required, permission_required
from src.web.handlers.maintenance import maintenance_protected

tag_bp = Blueprint('tag', __name__, url_prefix='/tags', template_folder='../templates')

@tag_bp.route("/list", methods=["GET"])
@login_required
@permission_required("user_index")
@maintenance_protected("admin")
def list():
    """
    Muestra una lista paginada de etiquetas.

    Requiere que el usuario esté autenticado, tenga permiso
    para listar usuarios y que el sistema no esté en modo mantenimiento.

    Query Parameters:
        page (int): Número de página (por defecto: 1).
        order_by (str): Campo por el cual ordenar (por defecto: "fecha_creacion").
        order_dir (str): Dirección de orden ("asc" o "desc", por defecto: "desc").
        busqueda (str, optional): Texto de búsqueda parcial por nombre de etiqueta.

    Returns:
        str: Renderizado de la plantilla `tags.html` con los resultados paginados.
    """
    page = request.args.get("page", 1, type=int)
    order_by = request.args.get("order_by", "fecha_creacion")
    order_dir = request.args.get("order_dir", "desc")
    busqueda = request.args.get("busqueda")

    pagination = list_tags(
        page=page,
        per_page=25,
        busqueda=busqueda,
        order_by=order_by,
        order_dir=order_dir
    )

    tags = pagination.items
    return render_template("tags.html", tags=tags, pagination=pagination)


@maintenance_protected("admin")
@tag_bp.route('/add', methods=['POST'])
def add_tag():
    """
    Crea una nueva etiqueta (Tag) a partir del formulario de creación.

    Validaciones:
        - El campo "nombre" debe estar presente.
        - Debe tener entre 3 y 50 caracteres.
        - No debe existir otra etiqueta con el mismo slug.

    Si pasa las validaciones, se crea el Tag en la base de datos.

    Returns:
        Response: Redirección a la vista de lista con mensajes flash de éxito o error.
    """
    nombre = request.form.get('nombre')

    if not nombre:
        flash("Ingrese un nombre para el tag.", "danger")
        return redirect(url_for('tag.list'))

    if len(nombre) < 3 or len(nombre) > 50:
        flash("El nombre del tag debe tener entre 3 y 50 caracteres.", "danger")
        return redirect(url_for('tag.list'))

    slug = generate_slug(nombre)
    existe_tag = get_tag_by_slug(slug)

    if existe_tag:
        flash("El nombre del tag ya existe.", "danger")
        return redirect(url_for('tag.list'))

    data = {
        'nombre': nombre,
        'slug': slug
    }

    create_tag(data)

    flash("El tag se creó correctamente.", "success")
    return redirect(url_for('tag.list'))


@maintenance_protected("admin")
@tag_bp.route("/<int:tag_id>/delete", methods=['POST'])
def del_tag(tag_id):
    """
    Elimina una etiqueta existente si no está siendo utilizada por un sitio.

    Args:
        tag_id (int): ID de la etiqueta a eliminar.

    Returns:
        Response: Redirección con mensaje flash de éxito o error.
    """
    if used_tag(tag_id):
        flash("El tag no se puede eliminar debido a que un sitio lo está utilizando.", "danger")
        return redirect(url_for('tag.list'))

    delete_tag(tag_id)
    flash("El tag se eliminó correctamente.", "success")
    return redirect(url_for('tag.list'))


@maintenance_protected("admin")
@tag_bp.route("/<int:tag_id>/edit", methods=['POST'])
def edit_tag(tag_id):
    """
    Edita una etiqueta existente (nombre y slug).

    Validaciones:
        - El campo "nombre" debe estar presente.
        - Debe tener entre 3 y 50 caracteres.
        - No debe corresponder a otra etiqueta existente.

    Args:
        tag_id (int): ID de la etiqueta a editar.

    Returns:
        Response: Redirección con mensaje flash de éxito o error.
    """
    nombre = request.form.get('nombre')

    if not nombre:
        flash("Ingrese un nombre para el tag.", "danger")
        return redirect(url_for('tag.list'))

    if len(nombre) < 3 or len(nombre) > 50:
        flash("El nombre del tag debe tener entre 3 y 50 caracteres.", "danger")
        return redirect(url_for('tag.list'))

    existe_tag = get_tag_by_name(nombre)
    if existe_tag:
        flash("El nombre pertenece a un tag existente.", "danger")
        return redirect(url_for('tag.list'))

    update_tag(tag_id, nombre)
    flash("El tag se editó correctamente.", "success")
    return redirect(url_for('tag.list'))