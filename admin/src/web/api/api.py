from flask import Blueprint, jsonify, request
from sqlalchemy import or_, func, desc, asc
from src.core.database import db
from src.core.models.site import Sitio
from src.core.models.tag import Tag
from src.core.models.tag import sitios_tags


api_bp = Blueprint("api_public", __name__, url_prefix="/api")

# Endpoint de prueba para sitios
@api_bp.get("/sites/")
def get_sites():
    # 1. Preparar la consulta base (solo sitios visibles)
    query = db.session.query(Sitio).filter(Sitio.visible == True)

    # 2. Manejo de Búsqueda por Texto (Aplica sobre nombre y descripción breve)
    search_term = request.args.get('search')
    if search_term:
        search_like = f"%{search_term}%"
        # Usa 'or_' para buscar el término en cualquiera de los dos campos
        query = query.filter(or_(
            Sitio.nombre.ilike(search_like),
            Sitio.descripcion_breve.ilike(search_like)
        ))

    # 3. Manejo de Filtros
    ciudad = request.args.get('city')
    provincia = request.args.get('province')
    estado = request.args.get('state') # Estado de conservación
    
    if ciudad:
        query = query.filter(Sitio.ciudad.ilike(f"%{ciudad}%"))
    if provincia:
        query = query.filter(Sitio.provincia == provincia)
    if estado:
        query = query.filter(Sitio.estado_conservacion == estado)
        
    # 4. Manejo de Tags (Filtro por multiselección)
    tags_param = request.args.get('tags')
    if tags_param:
        # Convierte los IDs de tags separados por coma a una lista de enteros
        tag_ids = [int(tid) for tid in tags_param.split(',') if tid.isdigit()]
        if tag_ids:
            # Hace un JOIN y filtra los sitios que contienen CUALQUIERA de los IDs
            query = query.join(Sitio.tags).filter(Tag.id.in_(tag_ids))
            
    # 5. Manejo de Ordenamiento
    # 'registrado' por defecto, para cumplir el requisito de 'fecha de registro'
    order_by = request.args.get('order_by', 'registrado') 
    order_direction = request.args.get('order_dir', 'desc') # Por defecto: descendente (más reciente)

    sort_column = None
    if order_by == 'nombre':
        sort_column = Sitio.nombre
    elif order_by == 'registrado':
        sort_column = Sitio.registrado
    # Nota: Se omiten 'mejor rankeados' ya que eliminamos la dependencia de reviews.

    # Aplicar la dirección del orden
    if sort_column is not None:
        if order_direction == 'asc':
            query = query.order_by(asc(sort_column))
        else: # 'desc' o cualquier otro valor por defecto
            query = query.order_by(desc(sort_column))


    # 6. Ejecutar la consulta y formatear la respuesta
    sitios_data = query.all()

    data = [
        {
            "id": sitio.id,
            "name": sitio.nombre,
            "short_description": sitio.descripcion_breve,
            "city": sitio.ciudad,
            "province": sitio.provincia,
            "state_of_conservation": sitio.estado_conservacion,
            "registered_date": sitio.registrado.strftime('%Y-%m-%d'), 
            # Incluir tags asociados (mostrar 5 máximo, como pide la consigna)
            "tags": [{"id": t.id, "name": t.name} for t in sitio.tags[:5]], 
            "image_url": "/img/default.jpg", # URL de imagen de portada (placeholder)
        }
        for sitio in sitios_data
    ]

    return jsonify({"data": data, "total": len(data)})
