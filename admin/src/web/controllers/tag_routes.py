#gestion de las etiquetas o categorias de los sitios historicos

#ej crear etiquetas, editar, eliminar etiquetas y asociarlas a los sitios.

#sujeto a modificaciones

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.core.tag_service import generate_slug, get_tag_by_slug, create_tag, list_tags, delete_tag, update_tag, get_tag_by_name
from src.core.models import Tag
from src.web.handlers.auth import login_required, permission_required
from src.web.handlers.maintenance import maintenance_protected
tag_bp = Blueprint('tag', __name__, url_prefix='/tags', template_folder='../templates')

@tag_bp.route("/list", methods=["GET"])
@login_required
@permission_required("user_index")
@maintenance_protected("admin")
def list():
    page = request.args.get("page", 1, type=int)
    search_nombre = request.args.get("nombre")
    search_slug = request.args.get("slug")
    order_by = request.args.get("order_by", "fecha_creacion")
    order_dir = request.args.get("order_dir", "desc")
    
    pagination = list_tags(
        page=page,
        per_page=25,
        search_nombre=search_nombre,
        search_slug=search_slug,
        order_by=order_by,
        order_dir=order_dir
    )
    tags = pagination.items
    return render_template("tags.html", tags=tags, pagination=pagination)

@maintenance_protected("admin")
@tag_bp.route('/add', methods=['POST'])
def add_tag():

    nombre = request.form.get('nombre')

    #verifico que esten todos los campos
    if not nombre:
        flash("Ingrese un nombre para el tag.", "danger")
        return redirect(url_for('tag.list'))
        
    #verifico que tenga entre 3 y 50 caracteres
    if len(nombre) < 3 or len(nombre) > 50:
        flash("El nombre del tag debe tener entre 3 y 50 caracteres.", "danger")
        return redirect(url_for('tag.list'))
    
    #verifico que no exista el tag, aplicando el case insensitive generando el slug y comparandolo
    slug = generate_slug(nombre)
    existe_tag = get_tag_by_slug(slug)
        
    if existe_tag:
        flash("El nombre del tag ya existe.", "danger")
        return redirect(url_for('tag.list'))
        
    #guardo la data y creo el tag
    data = {
        'nombre' : nombre,
        'slug' : slug
    }

    create_tag(data)

    flash("El tag se creo correctamente.", "success")
    return redirect(url_for('tag.list'))

@maintenance_protected("admin")
@tag_bp.route("/<int:tag_id>/delete", methods=['POST'])
def del_tag(tag_id):

    #falta condicion de que no este asignado a un sitio historico

    delete_tag(tag_id)

    flash("El tag se elimino correctamente.", "success")
    return redirect(url_for('tag.list'))

@maintenance_protected("admin")
@tag_bp.route("/<int:tag_id>/edit", methods=['POST'])
def edit_tag(tag_id):

    nombre = request.form.get('nombre')
    #checkeo que haya ingresado nombre
    if not nombre:
        flash("Ingrese un nombre para el tag.", "danger")
        return redirect(url_for('tag.list'))
    
    #verifico que tenga entre 3 y 50 caracteres
    if len(nombre) < 3 or len(nombre) > 50:
        flash("El nombre del tag debe tener entre 3 y 50 caracteres.", "danger")
        return redirect(url_for('tag.list'))
    
    #checkeo que el nombre no corresponda a otro tag
    existe_tag = get_tag_by_name(nombre)
    if existe_tag:
        flash("El nombre pertenece a un tag existente.", "danger")
        return redirect(url_for('tag.list'))
    
    update_tag(tag_id, nombre)

    flash("El tag se edito correctamente.", "success")
    return redirect(url_for('tag.list'))