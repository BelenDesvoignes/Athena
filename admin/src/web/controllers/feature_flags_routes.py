from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from datetime import datetime, timezone, timedelta
from src.core.database import db
from src.core.models.feature_flags import FeatureFlag
from src.web.handlers.auth import login_required, permission_required
from src.core.models.user import User

feature_flags_bp = Blueprint("feature_flags", __name__, url_prefix="/admin/feature-flags")


@feature_flags_bp.route("/maintenance/admin")
def maintenance_admin():
    """
    Muestra la página de mantenimiento del área de administración.
    
    Returns:
        Renderiza el template 'maintenance_admin.html' con el mensaje correspondiente.
    """
    msg = g.feature_flags_msg.get("admin_maintenance_mode")
    return render_template(
        "maintenance_admin.html",
        message=msg or "El área de administración está en mantenimiento."
    )

@feature_flags_bp.route("/maintenance/portal")
def maintenance_portal():
    """
    Muestra la página de mantenimiento del portal web.

    Returns:
        Renderiza el template 'maintenance_portal.html' con el mensaje correspondiente.
    """
    msg = g.feature_flags_msg.get("portal_maintenance_mode")
    return render_template(
        "maintenance_portal.html",
        message=msg or "El portal está en mantenimiento."
    )

@feature_flags_bp.route("/", methods=["GET"])
@permission_required("feature_flags_manage")
def index():
    """
    Lista todos los feature flags ordenados por ID.

    Returns:
        Renderiza el template 'feature_flags.html' con la lista de flags.
    """
    flags = db.session.execute(
            db.select(FeatureFlag).order_by(FeatureFlag.id)
            ).scalars().all()   
    db.session.commit()  
    db.session.expire_all()  
    return render_template("feature_flags.html", flags=flags)


def _has_changes(flag, new_value, new_message):
    """
    Comprueba si hubo cambios en el estado o mensaje de un flag.

    Args:
        flag (FeatureFlag): El flag a comparar.
        new_value (bool): Nuevo valor de 'is_enabled'.
        new_message (str): Nuevo mensaje de mantenimiento.

    Returns:
        bool: True si hay cambios, False si no.
    """
    current_message = flag.maintenance_message or ""
    return flag.is_enabled != new_value or current_message != (new_message or "")

def _validate_message(flag, new_value, new_message):
    """
    Valida el mensaje de mantenimiento si el flag corresponde a modo mantenimiento.

    Args:
        flag (FeatureFlag): El flag a validar.
        new_value (bool): Nuevo valor de 'is_enabled'.
        new_message (str): Nuevo mensaje de mantenimiento.

    Returns:
        bool: True si el mensaje es válido o no aplica, False si hay error.
    """
    if flag.key in ["admin_maintenance_mode", "portal_maintenance_mode"]:
        if new_value and not new_message:
            flash(f"El flag '{flag.display_name}' requiere un mensaje de mantenimiento.", "danger")
            return False
        if new_message and len(new_message) > 255:
            flash("El mensaje de mantenimiento no puede superar los 255 caracteres.", "danger")
            return False
    return True

@feature_flags_bp.route("/update-all", methods=["POST"])
@login_required
@permission_required("feature_flags_manage")
def update_all():
    """
    Actualiza todos los feature flags según los valores enviados desde el formulario.

    Modifica 'is_enabled', 'maintenance_message', 'last_modified_at' y 'last_modified_by'.

    Returns:
        Redirige a la página de lista de feature flags y muestra un mensaje flash.
    """
    arg_tz = timezone(timedelta(hours=-3))
    try:
        flags = db.session.execute(db.select(FeatureFlag).order_by(FeatureFlag.id)).scalars().all()
        user_id = session.get("user_id")
        user = db.session.get(User, user_id)

        any_changes = False

        for flag in flags:
            new_value = request.form.get(f"flag_{flag.id}") == "true"
            new_message = request.form.get(f"message_{flag.id}", "").strip() if flag.key in ["admin_maintenance_mode", "portal_maintenance_mode"] else None

            if _has_changes(flag, new_value, new_message):
                if not _validate_message(flag, new_value, new_message):
                    return redirect(url_for("feature_flags.index"))
                flag.is_enabled = new_value
                flag.maintenance_message = new_message if new_message else None
                flag.last_modified_at = datetime.now(arg_tz)
                flag.last_modified_by = user.id if user else None
                any_changes = True

        if not any_changes:
            flash("No se realizaron cambios en los feature flags.", "info")
            return redirect(url_for("feature_flags.index"))

        db.session.commit()
        flash("Los cambios en los feature flags fueron guardados correctamente.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar los feature flags: {e}", "danger")

    return redirect(url_for("feature_flags.index"))

