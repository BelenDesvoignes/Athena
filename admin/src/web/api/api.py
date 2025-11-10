from flask import Blueprint, jsonify
# Importamos el objeto 'db' del core/database, que contiene la sesión
from src.core.database import db 
from src.core.models.site import Sitio
from sqlalchemy import func
from src.core.models.review import Review, ReviewStatus

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Endpoint de prueba para sitios
@api_bp.get("/sites/")
def get_sites():
    # Usamos db.session.query() en lugar de db_session.query()
    sitios = (
        db.session.query( 
            Sitio.id,
            Sitio.nombre,
            Sitio.ciudad,
            Sitio.provincia,
            func.avg(Review.rating).label("promedio_rating"),
        )
        # La convención de nombres en tus modelos puede ser 'site_id' y 'Sitio.id'
        # Lo dejo como está ya que asumo que las relaciones ORM ya están definidas
        .join(Review, Review.site_id == Sitio.id, isouter=True)
        .filter((Review.status == ReviewStatus.APROBADA) | (Review.status == None))
        .group_by(Sitio.id, Sitio.nombre, Sitio.ciudad, Sitio.provincia) # Agregamos columnas faltantes para Postgres/SQLAlchemy 2.0
        .all()
    )


    data = [
        {
            "id": sitio.id,
            "name": sitio.nombre,
            "city": sitio.ciudad,
            "province": sitio.provincia,
            "rating": round(sitio.promedio_rating or 0, 1),  
            "image_url": "/img/default.jpg",  
        }
        for sitio in sitios
    ]

    return jsonify(data)
