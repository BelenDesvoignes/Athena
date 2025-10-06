from flask import redirect, url_for, session, g, request, g
from src.core.database import db
from src.core.models.user import User
from src.core.models.feature_flags import FeatureFlag
from functools import wraps

def maintenance_check(app):
    @app.before_request
    def load_feature_flags():
        flags = db.session.execute(db.select(FeatureFlag)).scalars().all()
        g.feature_flags = {f.key: f.is_enabled for f in flags}
        g.feature_flags_msg = {f.key: f.maintenance_message for f in flags}

        user = getattr(g, "user", None)
        endpoint = request.endpoint or ""

        maintenance_endpoints = [
            "maintenance_admin", "maintenance_portal",
            "auth.login", "auth.logout"
        ]

        if endpoint in maintenance_endpoints:
            return  

        if g.feature_flags.get("admin_maintenance_mode"):
            if "admin" in endpoint and (user or 'user_id' in session):
                return redirect(url_for("maintenance_admin"))

        if g.feature_flags.get("portal_maintenance_mode"):
            if "portal" in endpoint and (user or 'user_id' in session):
                return redirect(url_for("maintenance_portal"))



def maintenance_protected(area: str):
    """
    area: "admin" o "portal"
    Bloquea el endpoint si el modo de mantenimiento correspondiente está activo.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Asegurarse de que los flags estén cargados
            if not hasattr(g, "feature_flags"):
                return f(*args, **kwargs)
            
            if area == "admin" and g.feature_flags.get("admin_maintenance_mode"):
                if 'user_id' in session:
                    return redirect(url_for("maintenance_admin"))
            elif area == "portal" and g.feature_flags.get("portal_maintenance_mode"):
                return redirect(url_for("maintenance_portal"))

            return f(*args, **kwargs)
        return wrapped
    return decorator