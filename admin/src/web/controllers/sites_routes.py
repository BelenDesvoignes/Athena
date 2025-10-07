from flask import (
    Blueprint,
    render_template,
    request,
    Response,
    redirect,
    url_for,
    flash,
    abort,
    send_file,
    session,
)
import csv
from io import StringIO
from datetime import datetime
from sqlalchemy import func
from src.core.models.site import Sitio
from src.core.models.user import User
from shapely.wkt import loads
from src.core.database import db
from src.web.handlers.auth import login_required, permission_required
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape


"""Controlador para la gestión de sitios turísticos."""
""" Ruta basica para sitios turísticos. """
bp_sitios = Blueprint("sitios", __name__, url_prefix="/sitios")

"""Listado de sitios turísticos con paginación y búsqueda avanzada"""


@bp_sitios.route("/")
@login_required
def list():

    page = request.args.get("page", 1, type=int)
    sitios = db.session.query(Sitio).paginate(page=page, per_page=25)

    current_user = get_current_user()
    return render_template("sites_list.html", sitios=sitios, current_user=current_user)


"""Procedimiento para crear un nuevo sitio turístico"""


@bp_sitios.route("/nuevo", methods=["GET", "POST"])
@login_required
def new():
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
        ubicacion = WKTElement(f"POINT({longitud} {latitud})", srid=4326)
        """ Validaciones básicas de los campos """
        if not all(
            [
                nombre,
                descripcion_breve,
                descripcion_completa,
                ciudad,
                provincia,
                estado_conservacion,
                inauguracion,
                categoria,
                ubicacion,
            ]
        ):
            error = "Todos los campos son obligatorios."
            return render_template("new_site.html", error=error)

        try:
            ubicacion = WKTElement(f"POINT({longitud} {latitud})", srid=4326)

            sitio = Sitio(
                nombre=nombre,
                descripcion_breve=descripcion_breve,
                descripcion_completa=descripcion_completa,
                ciudad=ciudad,
                provincia=provincia,
                ubicacion=ubicacion,
                estado_conservacion=estado_conservacion,
                inauguracion=int(inauguracion),
                categoria=categoria,
                visible=visible,
            )
            db.session.add(sitio)
            db.session.commit()
            flash("Sitio creado correctamente")
            return redirect(url_for("sitios.list"))
        except Exception as e:
            error = f"Error al crear el sitio: {str(e)}"
            db.session.rollback()
            return render_template("new_site.html", error=error)

    return render_template("new_site.html")


"""Detalle de un sitio turístico"""

@login_required
@bp_sitios.route("/<int:id>/detalle", methods=["GET"])
def detail(id):
    sitio = db.session.get(Sitio, id)
    if not sitio:
        abort(404, "Sitio no encontrado.")

    coordenadas = extract_coords(sitio.ubicacion)

    current_user = get_current_user()
    

    return render_template(
        "site_detail.html",
        sitio=sitio,
        current_user=current_user,
        coordenadas=coordenadas
    )
"""Logica para editar un sitio turístico existente"""
@bp_sitios.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
def edit(id):
    current_user = get_current_user()
    if not current_user or not is_editor_or_admin(current_user):
        abort(401, "No tienes permisos para editar sitios.")
    sitio = db.session.get(Sitio, id)
    if not sitio:
        abort(404, "Sitio no encontrado.")

    error = None

    if request.method == "POST":
        sitio.nombre = request.form.get("nombre", sitio.nombre)
        sitio.descripcion_breve = request.form.get("descripcion_breve", sitio.descripcion_breve)
        sitio.descripcion_completa = request.form.get("descripcion_completa", sitio.descripcion_completa)
        sitio.ciudad = request.form.get("ciudad", sitio.ciudad)
        sitio.provincia = request.form.get("provincia", sitio.provincia)
        sitio.estado_conservacion = request.form.get("estado_conservacion", sitio.estado_conservacion)
        sitio.inauguracion = int(request.form.get("inauguracion", sitio.inauguracion))
        sitio.categoria = request.form.get("categoria", sitio.categoria)
        sitio.visible = bool(request.form.get("visible", sitio.visible))

        latitud = request.form.get("latitud", None)
        longitud = request.form.get("longitud", None)
        if latitud and longitud:
            sitio.ubicacion = WKTElement(f"POINT({longitud} {latitud})", srid=4326)

        # Validación de campos obligatorios
        if not all([
            sitio.nombre,
            sitio.descripcion_breve,
            sitio.descripcion_completa,
            sitio.ciudad,
            sitio.provincia,
            sitio.estado_conservacion,
            sitio.inauguracion,
            sitio.categoria,
            sitio.ubicacion,
        ]):
            error = "Todos los campos son obligatorios."
            return render_template("edit_site.html", sitio=sitio, error=error, latitud=latitud or sitio.latitud, longitud=longitud or sitio.longitud, current_user=current_user)

        db.session.commit()
        flash("Sitio actualizado correctamente")
        return redirect(url_for("sitios.list"))
    
    coordenadas = extract_coords(sitio.ubicacion)
    return render_template("edit_site.html", sitio=sitio,coordenadas=coordenadas, current_user=current_user)




@bp_sitios.route("/<int:id>/eliminar", methods=["POST"])
def remove(id):
    current_user = get_current_user()
    if not current_user or not is_admin(current_user):
        abort(401, "Solo administradores pueden eliminar sitios.")
    sitio = db.session.get(Sitio, id)
    if not sitio:
        abort(404)
    db.session.delete(sitio)
    db.session.commit()
    flash("Sitio eliminado")
    return redirect(url_for("sitios.list"))


""" Logica para la exportacion de sitios a CSV """

@bp_sitios.route("/exportar", methods=["GET"])
@login_required
def export():
    # Consulta con extracción de coordenadas usando func.ST_X y func.ST_Y
    sitios = db.session.query(
        Sitio,
        func.ST_Y(Sitio.ubicacion).label("latitud"),
        func.ST_X(Sitio.ubicacion).label("longitud"),
    ).all()
    si = StringIO()
    writer = csv.writer(si)

    writer.writerow(
        [
            "ID",
            "Nombre",
            "Descripción breve",
            "Descripción completa",
            "Ciudad",
            "Provincia",
            "Latitud",
            "Longitud",
            "Estado de conservación",
            "Año de inauguración",
            "Categoría",
            "Visible",
        ]
    )
    for sitio, lat, lng in sitios:
        writer.writerow(
            [
                sitio.id,
                sitio.nombre,
                sitio.descripcion_breve,
                sitio.descripcion_completa,
                sitio.ciudad,
                sitio.provincia,
                lat if lat is not None else "",
                lng if lng is not None else "",
                getattr(sitio, "estado_conservacion", ""),
                getattr(sitio, "inauguracion", ""),
                getattr(sitio, "categoria", ""),
                "Sí" if sitio.visible else "No",
            ]
        )
    output = si.getvalue()
    filename = f"sitios_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"},
    )


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


def is_admin(user):
    return user.role_id == 1


def is_editor_or_admin(user):
    return user.role_id in [1, 2]


def extract_coords(ubicacion):
    geom = to_shape(ubicacion)

    resultado = {'latitud': float(geom.y), 'longitud': float(geom.x)}
    
    return resultado