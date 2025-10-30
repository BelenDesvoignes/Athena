from flask import Blueprint, jsonify

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Endpoint de prueba para sitios
@api_bp.get("/sites")
def get_sites():
    # Esto normalmente vendría de tu base de datos
    sitios = [
        {"id": 1, "name": "Fortín Histórico", "city": "Córdoba", "province": "Córdoba", "rating": 4.5, "image_url": "/img/fortin.jpg"},
        {"id": 2, "name": "Museo Colonial", "city": "Buenos Aires", "province": "Buenos Aires", "rating": 4.8, "image_url": "/img/museo.jpg"}
    ]
    return jsonify(sitios)
