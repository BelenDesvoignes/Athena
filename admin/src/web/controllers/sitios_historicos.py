from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from src.core.models.sitios import Sitio
from src.core.database import db

bp_sitios = Blueprint("sitios", __name__, url_prefix="/sitios")

@bp_sitios.route("/")
def listado():
    # Implementar búsqueda avanzada y paginación aquí
    page = request.args.get("page", 1, type=int)
    sitios = db.session.query(Sitio).paginate(page=page, per_page=25)
    return render_template("sitios/listado.html", sitios=sitios)

@bp_sitios.route("/nuevo", methods=["GET", "POST"])
def create_sitio(current_user):
    if not is_editor_or_admin(current_user):
        abort(401, "No tienes permisos para crear sitios.")
    # ... lógica para crear sitio ...
    # sitio = Sitio(...)
    # db.session.add(sitio)
    # db.session.commit()
    # return sitio

@bp_sitios.route("/<int:id>/editar", methods=["GET", "POST"])
@bp_sitios.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    # Suponiendo que tienes acceso al usuario actual como current_user
    from flask_login import current_user  # Si usas flask-login

    if not is_editor_or_admin(current_user):
        abort(401, "No tienes permisos para editar sitios.")

    sitio = db.session.get(Sitio, id)
    if not sitio:
        abort(404, "Sitio no encontrado.")

    if request.method == "POST":
        # Validar y actualizar campos
        sitio.nombre = request.form.get("nombre", sitio.nombre)
        sitio.descripcion_breve = request.form.get("descripcion_breve", sitio.descripcion_breve)
        sitio.descripcion_completa = request.form.get("descripcion_completa", sitio.descripcion_completa)
        sitio.ciudad = request.form.get("ciudad", sitio.ciudad)
        sitio.provincia = request.form.get("provincia", sitio.provincia)
        sitio.latitud = float(request.form.get("latitud", sitio.latitud))
        sitio.longitud = float(request.form.get("longitud", sitio.longitud))
        sitio.estado_conservacion = request.form.get("estado_conservacion", sitio.estado_conservacion)
        sitio.inauguracion = int(request.form.get("inauguracion", sitio.inauguracion))
        sitio.categoria = request.form.get("categoria", sitio.categoria)
        sitio.visible = bool(request.form.get("visible", sitio.visible))

        if not all([sitio.nombre, sitio.descripcion_breve, sitio.descripcion_completa, sitio.ciudad,
                    sitio.provincia, sitio.latitud, sitio.longitud, sitio.estado_conservacion,
                    sitio.inauguracion, sitio.categoria,sitio.visible]):
            return render_template(
                "editar_sitio.html", error="Todos los campos son obligatorios."
            )

        db.session.commit()
        flash("Sitio actualizado correctamente")
        return redirect(url_for("sitios.listado"))

    return render_template("sitios/form.html", sitio=sitio)


@bp_sitios.route("/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    # Solo administradores
    sitio = db.session.get(Sitio, id)
    if not sitio:
        abort(404)
    db.session.delete(sitio)
    db.session.commit()
    flash("Sitio eliminado")
    return redirect(url_for("sitios.listado"))





def is_admin(user):
    return user.role.name == "admin"

def is_editor_or_admin(user):
    return user.role.name in ["admin", "editor"]