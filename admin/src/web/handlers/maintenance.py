from functools import wraps
from flask import g, redirect, request, session, url_for, jsonify

from src.core.database import db
from src.core.models.feature_flags import FeatureFlag


def maintenance_check(app):
    @app.before_request
    def load_feature_flags():
        flags = db.session.execute(db.select(FeatureFlag)).scalars().all()
        g.feature_flags = {f.key: f.is_enabled for f in flags}
        g.feature_flags_msg = {f.key: f.maintenance_message for f in flags}

        user = getattr(g, "user", None)
        endpoint = request.endpoint or ""

        maintenance_endpoints = [
            "feature_flags.maintenance_admin",
            "feature_flags.maintenance_portal",
            "auth.login", "auth.logout"
        ]

        if endpoint in maintenance_endpoints:
            return  

        if g.feature_flags.get("admin_maintenance_mode"):
            if "admin" in endpoint and (user or 'user_id' in session):
                return redirect(url_for("feature_flags.maintenance_admin"))


def maintenance_protected(area: str):
    """
    area: "admin"
    Bloquea el endpoint si el modo de mantenimiento correspondiente está activo.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            
            if not hasattr(g, "feature_flags"):
                return f(*args, **kwargs)
            
            if area == "admin" and g.feature_flags.get("admin_maintenance_mode"):
                return redirect(url_for("feature_flags.maintenance_admin"))
            elif area == "portal" and g.feature_flags.get("portal_maintenance_mode"):
                return redirect(url_for("feature_flags.maintenance_portal"))

            return f(*args, **kwargs)
        return wrapped
    return decorator


def reviews_enabled_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        reviews_disabled = g.feature_flags.get("reviews_disabled", False)

        if reviews_disabled:
            return jsonify({
                "error": "Las reseñas están deshabilitadas temporalmente.",
                "flag": "reviews_disabled"
            }), 403 

        return f(*args, **kwargs)
    return decorated_function