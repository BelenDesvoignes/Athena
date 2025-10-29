from datetime import datetime, timedelta, timezone
from io import StringIO
import csv

from flask import Blueprint, abort, flash, redirect, render_template, request, Response, session, url_for, current_app
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from sqlalchemy import func, or_

from src.core.database import db
from src.core.models.modification_history import ModificationHistory
from src.core.models.site import Sitio
from src.core.models.tag import Tag, sitios_tags
from src.core.models.user import User
from src.core.models.images import Imagen
from src.web.handlers.auth import login_required, permission_required
from src.web.handlers.maintenance import maintenance_protected

from minio import Minio
from werkzeug.utils import secure_filename
import uuid

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024 

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


"""Controlador para la gestión de sitios turísticos."""
""" Ruta basica para sitios turísticos. """
bp_sitios = Blueprint("sitios", __name__, url_prefix="/sitios")

"""Listado de sitios turísticos con paginación y búsqueda avanzada"""


@bp_sitios.route("/", methods=["GET"])
@login_required
@permission_required("site_list")
@maintenance_protected("admin")
def list():
    page = request.args.get("page", 1, type=int)
    order_by = request.args.get("order_by", "nombre")
    order_dir = request.args.get("order_dir", "asc")

    query = db.session.query(Sitio)

    ciudad = request.args.get("ciudad")
    provincia = request.args.get("provincia")
    tags_seleccionados = request.args.getlist("tag[]")
    conservacion = request.args.get("conservacion")
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    visibilidad = request.args.get("visibilidad")
    busqueda = request.args.get("busqueda")

    # Filtros existentes
    if ciudad:
        query = query.filter(Sitio.ciudad == ciudad)
    if provincia:
        query = query.filter(Sitio.provincia == provincia)
    if tags_seleccionados:
        query = (
            query.join(sitios_tags, Sitio.id == sitios_tags.c.sitio_id)
                 .join(Tag, Tag.id == sitios_tags.c.tag_id)
                 .filter(Tag.nombre.in_(tags_seleccionados))
                 .distinct()
        )
    if conservacion:
        query = query.filter(Sitio.estado_conservacion == conservacion)
    if desde:
        desde_dt = datetime.strptime(desde, "%Y-%m-%d")
        query = query.filter(Sitio.registrado >= desde_dt)
    if hasta:
        hasta_dt = datetime.strptime(hasta, "%Y-%m-%d") + timedelta(days=1)
        query = query.filter(Sitio.registrado < hasta_dt)
    if visibilidad:
        query = query.filter(Sitio.visible == "true")
    if busqueda:
        query = query.filter(
            or_(
                Sitio.nombre.ilike(f"%{busqueda}%"),
                Sitio.descripcion_breve.ilike(f"%{busqueda}%"),
                Sitio.descripcion_completa.ilike(f"%{busqueda}%"),
            )
        )

    if order_by == "ciudad":
        columna = Sitio.ciudad
    elif order_by == "registrado":
        columna = Sitio.registrado
    else:
        columna = Sitio.nombre

    if order_dir == "desc":
        query = query.order_by(columna.desc())
    else:
        query = query.order_by(columna.asc())

    sitios = query.paginate(page=page, per_page=25)

    provincias = [p[0] for p in db.session.query(Sitio.provincia).distinct().all()]
    ciudades = [p[0] for p in db.session.query(Sitio.ciudad).distinct().all()]
    tags = [p[0] for p in db.session.query(Tag.nombre).distinct().all()]

    current_user = get_current_user()
    return render_template(
        "sites_list.html",
        sitios=sitios,
        current_user=current_user,
        provincias=provincias,
        ciudades=ciudades,
        tags=tags,
    )


"""Procedimiento para crear un nuevo sitio turístico"""

@bp_sitios.route("/nuevo", methods=["GET", "POST"])
@login_required
@permission_required("site_new")
@maintenance_protected("admin")
def new():
    current_user = get_current_user()
    error = None
    tags = db.session.query(Tag).all()

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
        tag_ids = request.form.getlist("tags")
        visible = bool(request.form.get("visible"))
        ubicacion = WKTElement(f"POINT({longitud} {latitud})", srid=4326)

        if not all([
            nombre, descripcion_breve, descripcion_completa, ciudad, provincia,
            estado_conservacion, inauguracion, categoria, ubicacion
        ]):
            error = "No completaste todos los campos obligatorios."
            return render_template("new_site.html", tags=tags, error=error)

        try:
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
                tags=db.session.query(Tag).filter(Tag.id.in_(tag_ids)).all(),
                visible=visible,
            )
            db.session.add(sitio)
            db.session.flush()  # Para tener sitio.id antes de commit

            # --- Manejo de imágenes ---
            minio_client = Minio(
                endpoint=current_app.config["MINIO_SERVER"],
                access_key=current_app.config["MINIO_ACCESS_KEY"],
                secret_key=current_app.config["MINIO_SECRET_KEY"],
                secure=current_app.config["MINIO_SECURE"],
            )

            imagenes = request.files.getlist("imagenes")
            portada_form = request.form.getlist("portada")  # Índice de portada enviado
            portada_idx = int(portada_form[0]) if portada_form else 0

            if imagenes:
                if len(imagenes) > 10:
                    error = "No se pueden subir más de 10 imágenes."
                    db.session.rollback()
                    return render_template("new_site.html", tags=tags, error=error)

                for idx, file in enumerate(imagenes):
                    if not allowed_file(file.filename):
                        error = f"Formato no permitido: {file.filename}"
                        db.session.rollback()
                        return render_template("new_site.html", tags=tags, error=error)

                    file.seek(0, 2)
                    size = file.tell()
                    file.seek(0)

                    if size > MAX_IMAGE_SIZE:
                        error = f"Archivo demasiado grande: {file.filename}"
                        db.session.rollback()
                        return render_template("new_site.html", tags=tags, error=error)

                    ext = file.filename.rsplit(".", 1)[1].lower()
                    filename = f"{uuid.uuid4().hex}.{ext}"

                    minio_client.put_object(
                        bucket_name=current_app.config["MINIO_BUCKET"],
                        object_name=filename,
                        data=file,
                        length=size,
                        content_type=file.mimetype,
                    )

                    imagen = Imagen(
                        sitio_id=sitio.id,
                        ruta=f"{current_app.config['MINIO_BUCKET']}/{filename}",
                        titulo=secure_filename(file.filename),
                        descripcion="",
                        orden=idx,
                        es_portada=(idx == portada_idx)
                    )
                    db.session.add(imagen)

            db.session.commit()
            registrar_modificacion(sitio, current_user, "Creación")
            flash("Sitio creado correctamente")
            return redirect(url_for("sitios.list"))

        except Exception as e:
            db.session.rollback()
            error = f"Error al crear el sitio: {str(e)}"
            print(f"[DEBUG] Exception: {error}")
            return render_template("new_site.html", tags=tags, error=error)

    return render_template("new_site.html", tags=tags, current_user=current_user)


def get_modification_history(sitio_id, usuario_nombre="", tipo_accion="", desde="", hasta="", page=1):
    """
    Obtiene el historial de modificaciones de un sitio aplicando filtros opcionales.

    Args:
        sitio_id (int)
        usuario_nombre (str)
        tipo_accion (str)
        desde (str, formato 'YYYY-MM-DD')
        hasta (str, formato 'YYYY-MM-DD')
        page (int)

    Returns:
        Pagination: objeto de paginación con los resultados.
    """
    query = db.session.query(ModificationHistory).filter_by(sitio_id=sitio_id)

    if usuario_nombre:
        query = query.join(User).filter(User.nombre.ilike(f"%{usuario_nombre}%"))
    if tipo_accion:
        query = query.filter(ModificationHistory.tipo_accion == tipo_accion)
    if desde:
        query = query.filter(ModificationHistory.fecha_modificacion >= desde)
    if hasta:
        query = query.filter(ModificationHistory.fecha_modificacion < hasta + " 23:59:59")

    query = query.order_by(ModificationHistory.fecha_modificacion.desc())
    return query.paginate(page=page, per_page=25)

@bp_sitios.route("/<int:id>/detalle", methods=["GET"])
@maintenance_protected("admin")
@login_required
@permission_required("site_detail")
def detail(id):
    """
    Muestra el detalle de un sitio y su historial de modificaciones.

    Args:
        id (int): ID del sitio a visualizar.

    Returns:
        Response: Plantilla renderizada con los datos del sitio, sus coordenadas
        y el historial (filtrado o completo, según la validación).
    """
    sitio = db.session.get(Sitio, id)
    if not sitio:
        abort(404, "Sitio no encontrado.")

    coordenadas = extract_coords(sitio.ubicacion)
    current_user = get_current_user()

    desde = request.args.get("desde", "").strip()
    hasta = request.args.get("hasta", "").strip()
    usuario_nombre = request.args.get("usuario", "").strip()
    tipo_accion = request.args.get("tipo_accion", "").strip()
    page = request.args.get("page", 1, type=int)

    hoy = datetime.now().date()
    errores = False
    desde_dt = None
    hasta_dt = None

    if desde:
        try:
            desde_dt = datetime.strptime(desde, "%Y-%m-%d").date()
            if desde_dt > hoy:
                flash("La fecha 'Desde' no puede ser mayor a la fecha actual.", "warning")
                errores = True
        except ValueError:
            flash("Formato de fecha 'Desde' inválido. Use AAAA-MM-DD.", "warning")
            errores = True

    if hasta:
        try:
            hasta_dt = datetime.strptime(hasta, "%Y-%m-%d").date()
            if hasta_dt > hoy:
                flash("La fecha 'Hasta' no puede ser mayor a la fecha actual.", "warning")
                errores = True
        except ValueError:
            flash("Formato de fecha 'Hasta' inválido. Use AAAA-MM-DD.", "warning")
            errores = True

    if desde_dt and hasta_dt and desde_dt > hasta_dt:
        flash("La fecha 'Desde' no puede ser mayor que la fecha 'Hasta'.", "warning")
        errores = True

    if not errores:
        historial = get_modification_history(
            sitio_id=id,
            usuario_nombre=usuario_nombre,
            tipo_accion=tipo_accion,
            desde=desde,
            hasta=hasta,
            page=page
        )
    else:
        historial = get_modification_history(sitio_id=id, page=page)

    return render_template(
        "site_detail.html",
        sitio=sitio,
        current_user=current_user,
        coordenadas=coordenadas,
        historial=historial,
    )

"""Logica para editar un sitio turístico existente"""

@bp_sitios.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
@permission_required("site_update")
@maintenance_protected("admin")
def edit(id):
    sitio = db.session.get(Sitio, id)
    if not sitio:
        abort(404, "Sitio no encontrado.")
    current_user = get_current_user()
    error = None

    tags = db.session.query(Tag).all()

    if request.method == "POST":
        sitio.nombre = request.form.get("nombre", sitio.nombre)
        sitio.descripcion_breve = request.form.get(
            "descripcion_breve", sitio.descripcion_breve
        )
        sitio.descripcion_completa = request.form.get(
            "descripcion_completa", sitio.descripcion_completa
        )
        sitio.ciudad = request.form.get("ciudad", sitio.ciudad)
        sitio.provincia = request.form.get("provincia", sitio.provincia)
        sitio.estado_conservacion = request.form.get(
            "estado_conservacion", sitio.estado_conservacion
        )
        sitio.inauguracion = int(request.form.get("inauguracion", sitio.inauguracion))
        sitio.categoria = request.form.get("categoria", sitio.categoria)
        tag_ids = request.form.getlist("tags")
        sitio.tags = db.session.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        sitio.visible = bool(request.form.get("visible", sitio.visible))

        latitud = request.form.get("latitud", None)
        longitud = request.form.get("longitud", None)
        if latitud and longitud:
            sitio.ubicacion = WKTElement(f"POINT({longitud} {latitud})", srid=4326)

        """Validación de campos obligatorios"""
        if not all(
            [
                sitio.nombre,
                sitio.descripcion_breve,
                sitio.descripcion_completa,
                sitio.ciudad,
                sitio.provincia,
                sitio.estado_conservacion,
                sitio.inauguracion,
                sitio.categoria,
                sitio.ubicacion,
            ]
        ):
            error = "Todos los campos son obligatorios."
            return render_template(
                "edit_site.html",
                sitio=sitio,
                tags=tags,
                error=error,
                latitud=latitud or sitio.latitud,
                longitud=longitud or sitio.longitud,
                current_user=current_user,
            )

        db.session.commit()
        
        registrar_modificacion(sitio, current_user, "Edición")
        
        flash("Sitio actualizado correctamente")
        return redirect(url_for("sitios.list"))

    coordenadas = extract_coords(sitio.ubicacion)
    return render_template(
        "edit_site.html",
        sitio=sitio,
        tags=tags,
        coordenadas=coordenadas,
        current_user=current_user,
    )


"""Elimina un sitio turístico"""

@bp_sitios.route("/<int:id>/eliminar", methods=["POST"])
@login_required
@permission_required("site_delete")
@maintenance_protected("admin")
def remove(id):
    sitio = db.session.get(Sitio, id)
    if not sitio:
        abort(404)
    current_user = get_current_user()
    registrar_modificacion(sitio, current_user, "Eliminación")
    
    db.session.delete(sitio)
    db.session.commit()
    flash("Sitio eliminado")
    return redirect(url_for("sitios.list"))


""" Logica para la exportacion de sitios a CSV """

@bp_sitios.route("/exportar", methods=["GET"])
@login_required
@permission_required("export_csv")
@maintenance_protected("admin")
def export():
    sitios = db.session.query(
        Sitio,
        func.ST_Y(Sitio.ubicacion).label("latitud"),
        func.ST_X(Sitio.ubicacion).label("longitud"),
    ).all()
    if not sitios:
        flash("No hay sitios para exportar.")
        return redirect(url_for("sitios.list"))

    """Crear CSV en memoria"""
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

    resultado = {"latitud": float(geom.y), "longitud": float(geom.x)}

    return resultado

arg_tz = timezone(timedelta(hours=-3))
@maintenance_protected("admin")
def registrar_modificacion(sitio, usuario, tipo_accion):
    """
    Crea un registro en el historial de modificaciones para un sitio.

    Args:
        sitio: instancia del Sitio que se modificó (puede ser None si ya se eliminó)
        usuario: instancia del User que realizó la acción
        tipo_accion: str indicando la acción ('creación', 'edición', 'eliminación', etc.)
    """
    if not usuario or not tipo_accion:
        raise ValueError("Faltan parámetros obligatorios para registrar la modificación.")
    
    registro = ModificationHistory(
        sitio_id=sitio.id if sitio else None,
        sitio_nombre=sitio.nombre if sitio else "Sitio eliminado",
        usuario_id=usuario.id,
        tipo_accion=tipo_accion,
        fecha_modificacion=datetime.now(arg_tz)
    )
    db.session.add(registro)
    db.session.commit()
    