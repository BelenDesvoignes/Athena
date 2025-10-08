from functools import wraps
from flask import session
from src.core.database import db
from src.core.models.modification_history import ModificationHistory
from src.core.models.site import Sitio

def record_history(tipo_accion):
    """Decorador para registrar historial sin descripción"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            resultado = func(*args, **kwargs)

            sitio = None
            if "id" in kwargs:
                sitio = db.session.get(Sitio, kwargs["id"])
            elif isinstance(resultado, dict) and "sitio" in resultado:
                sitio = resultado["sitio"]

            usuario_id = session.get("user_id")

            if sitio and usuario_id:
                historial = ModificationHistory(
                    sitio_id=sitio.id,
                    usuario_id=usuario_id,
                    tipo_accion=tipo_accion
                )
                db.session.add(historial)
                db.session.commit()

            return resultado
        return wrapper
    return decorator