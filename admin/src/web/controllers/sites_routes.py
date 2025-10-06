from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    session,
)
from src.core.models.site import Sitio
from src.core.models.user import User
from src.core.database import db
from src.web.handlers.auth import login_required, permission_required
from geoalchemy2.types import Geometry
from shapely.geometry import Point

"""Controlador para la gestión de sitios turísticos."""
""" Ruta basica para sitios turísticos. """
bp_sitios = Blueprint("sitios", __name__, url_prefix="/sitios")

"""Listado de sitios turísticos con paginación y búsqueda avanzada"""
@bp_sitios.route("/")
@login_required
def listado():
 
    page = request.args.get("page", 1, type=int)
    sitios = db.session.query(Sitio).paginate(page=page, per_page=25)

    current_user = get_current_user()
    return render_template("sites_list.html", sitios=sitios, current_user=current_user)

"""Procedimiento para crear un nuevo sitio turístico"""
@bp_sitios.route("/nuevo", methods=["GET", "POST"])
@login_required
def create_sitio():
    current_user = get_current_user()
    if not current_user or not is_editor_or_admin(current_user):
        abort(401, "No tienes permisos para crear sitios.")

    error = None

    if request.method == "POST":
        nombre = request.form.get("nombre")
        descripcion_breve = request.form.get("descripcion_breve")
        descripcion_completa = request.form.get("descripcion_completa")
        ciudad = request.form.get("ciudad")
        provincia = request.form.get("provincia")
        latitud = request.form.get("latitud")
        longitud = request.form.get("longitud")
        estado_conservacion = request.form.get("estado_conservacion")
        inauguracion = request.form.get("inauguracion")
        categoria = request.form.get("categoria")
        visible = bool(request.form.get("visible"))

        """ Validaciones básicas de los campos """
        if not all(
            [
                nombre,
                descripcion_breve,
                descripcion_completa,
                ciudad,
                provincia,
                latitud,
                longitud,
                estado_conservacion,
                inauguracion,
                categoria,
            ]
        ):
            error = "Todos los campos son obligatorios."
            return render_template("new_site.html", error=error)

        try:
            latitud_float = float(latitud)
            longitud_float = float(longitud)
            ubicacion = from_shape(Point(longitud_float, latitud_float), srid=4326)

            sitio = Sitio(
                nombre=nombre,
                descripcion_breve=descripcion_breve,
                descripcion_completa=descripcion_completa,
                ciudad=ciudad,
                provincia=provincia,
                latitud=latitud_float,
                longitud=longitud_float,
                ubicacion=ubicacion,
                estado_conservacion=estado_conservacion,
                inauguracion=int(inauguracion),
                categoria=categoria,
                visible=visible,
            )
            db.session.add(sitio)
            db.session.commit()
            flash("Sitio creado correctamente")
            return redirect(url_for("sitios.listado"))
        except Exception as e:
            error = f"Error al crear el sitio: {str(e)}"
            db.session.rollback()
            return render_template("new_site.html", error=error)

    return render_template("new_site.html")

"""Detalle de un sitio turístico"""
@bp_sitios.route("/<int:id>/detalle", methods=["GET"])
def detalle(id):
    current_user = get_current_user()

    sitio = db.session.get(Sitio, id)
    if not sitio:
        abort(404, "Sitio no encontrado.")

    return render_template("site_detail.html", sitio=sitio, current_user=current_user)


@bp_sitios.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    current_user = get_current_user()
    if not current_user or not is_editor_or_admin(current_user):
        abort(401, "No tienes permisos para editar sitios.")
    sitio = db.session.get(Sitio, id)
    if not sitio:
        abort(404, "Sitio no encontrado.")
    if request.method == "POST":
        # Validar y actualizar campos
        sitio.nombre = request.form.get("nombre", sitio.nombre)
        sitio.descripcion_breve = request.form.get(
            "descripcion_breve", sitio.descripcion_breve
        )
        sitio.descripcion_completa = request.form.get(
            "descripcion_completa", sitio.descripcion_completa
        )
        sitio.ciudad = request.form.get("ciudad", sitio.ciudad)
        sitio.provincia = request.form.get("provincia", sitio.provincia)
        sitio.latitud = float(request.form.get("latitud", sitio.latitud))
        sitio.longitud = float(request.form.get("longitud", sitio.longitud))
        sitio.estado_conservacion = request.form.get(
            "estado_conservacion", sitio.estado_conservacion
        )
        sitio.inauguracion = int(request.form.get("inauguracion", sitio.inauguracion))
        sitio.categoria = request.form.get("categoria", sitio.categoria)
        sitio.visible = bool(request.form.get("visible", sitio.visible))

        if not all(
            [
                sitio.nombre,
                sitio.descripcion_breve,
                sitio.descripcion_completa,
                sitio.ciudad,
                sitio.provincia,
                sitio.latitud,
                sitio.longitud,
                sitio.estado_conservacion,
                sitio.inauguracion,
                sitio.categoria,
                sitio.visible,
            ]
        ):
            return render_template(
                "editar_sitio.html", error="Todos los campos son obligatorios."
            )

        db.session.commit()
        flash("Sitio actualizado correctamente")
        return redirect(url_for("sitios.listado"))

    return render_template("sitios/form.html", sitio=sitio)


@bp_sitios.route("/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    current_user = get_current_user()
    if not current_user or not is_admin(current_user):
        abort(401, "Solo administradores pueden eliminar sitios.")
    sitio = db.session.get(Sitio, id)
    if not sitio:
        abort(404)
    db.session.delete(sitio)
    db.session.commit()
    flash("Sitio eliminado")
    return redirect(url_for("sitios.listado"))


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


def is_admin(user):
    return user.role_id == 1


def is_editor_or_admin(user):
    return user.role_id in [1, 2]
