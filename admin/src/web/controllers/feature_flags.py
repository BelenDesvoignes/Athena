from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.web.handlers.auth import permission_required
from src.core.database import db
from src.core.models.feature_flags import FeatureFlag
from src.core.flags import get_flag_by_name

feature_flags_bp = Blueprint("feature_flags", __name__, url_prefix="/admin/feature-flags")


# 📌 Página principal: lista todos los feature flags
@feature_flags_bp.route("/", methods=["GET"])
@permission_required("feature_flags_manage")
def index():
    flags = db.session.execute(db.select(FeatureFlag)).scalars().all()
    return render_template("feature_flags.html", flags=flags)


# 📌 Alternar un flag (activar/desactivar)
@feature_flags_bp.route("/toggle/<string:flag_name>", methods=["POST"])
@permission_required("feature_flags_manage")
def toggle(flag_name):
    try:
        flag = get_flag_by_name(flag_name)
        new_value = request.form.get("value") == "true"
        flag.is_enabled = new_value
        db.session.commit()
        flash(f"El flag '{flag_name}' fue actualizado a {'ON' if new_value else 'OFF'}.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar el flag '{flag_name}': {e}", "danger")
    
    return redirect(url_for("feature_flags.index"))

@feature_flags_bp.route("/update_all", methods=["POST"])
@permission_required("feature_flags_manage")
def update_all():
    try:
        flags = db.session.execute(db.select(FeatureFlag)).scalars().all()

        for flag in flags:
            checkbox_name = f"flag_{flag.id}"
            flag.is_enabled = checkbox_name in request.form  # marcado → True, no marcado → False

        db.session.commit()
        flash("Todos los feature flags fueron actualizados correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar los feature flags: {e}", "danger")

    return redirect(url_for("feature_flags.index"))