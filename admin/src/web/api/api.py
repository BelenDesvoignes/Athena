from flask import Blueprint, jsonify, request
from sqlalchemy import or_, func, desc, asc, distinct
from src.core.database import db
from src.core.models.site import Sitio
from src.core.models.tag import Tag
from src.core.models.tag import sitios_tags


api_bp = Blueprint("api_public", __name__, url_prefix="/api")

# Endpoint de prueba para sitios
@api_bp.get("/sites/")
def get_sites():

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int) # 10 como default

    #  Preparar la consulta base (solo sitios visibles)
    query = db.session.query(Sitio).filter(Sitio.visible == True)

    # Manejo de Búsqueda por Texto (Aplica sobre nombre y descripción breve)
    search_term = request.args.get('search')
    if search_term:
        search_like = f"%{search_term}%"
        # Usa 'or_' para buscar el término en cualquiera de los dos campos
        query = query.filter(or_(
            Sitio.nombre.ilike(search_like),
            Sitio.descripcion_breve.ilike(search_like)
        ))

    #  Manejo de Filtros
    ciudad = request.args.get('city')
    provincia = request.args.get('province')
    estado = request.args.get('state') # Estado de conservación
    
    if ciudad:
        query = query.filter(Sitio.ciudad.ilike(f"%{ciudad}%"))
    if provincia:
        query = query.filter(Sitio.provincia == provincia)
    if estado:
        query = query.filter(Sitio.estado_conservacion == estado)
        
    # Manejo de Tags (Filtro por multiselección)
    tags_param = request.args.get('tags')
    if tags_param:
        # Convierte los IDs de tags separados por coma a una lista de enteros
        tag_ids = [int(tid) for tid in tags_param.split(',') if tid.isdigit()]
        if tag_ids:
            # Hace un JOIN y filtra los sitios que contienen CUALQUIERA de los IDs
            query = query.join(Sitio.tags).filter(Tag.id.in_(tag_ids))
            
    #  Manejo de Ordenamiento
    # 'registrado' por defecto, para cumplir el requisito de 'fecha de registro'
    order_by = request.args.get('order_by', 'registrado') 
    order_direction = request.args.get('order', 'desc') # Por defecto: descendente (más reciente)

    sort_column = None
    if order_by == 'nombre':
        sort_column = Sitio.nombre
    elif order_by == 'registrado':
        sort_column = Sitio.registrado

    # Aplicar la dirección del orden
    if sort_column is not None:
        if order_direction == 'asc':
            query = query.order_by(asc(sort_column))
        else: # 'desc' o cualquier otro valor por defecto
            query = query.order_by(desc(sort_column))


    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

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
            "tags": [{"id": t.id, "name": t.nombre} for t in sitio.tags[:5]], 
            "image_url": "/img/default.jpg", # URL de imagen de portada (placeholder)
        }
        for sitio in pagination.items
    ]

    return jsonify({
        "data": data,
        "total": pagination.total,
        "pages": pagination.pages,
        "page": pagination.page,
        "per_page": pagination.per_page,})


#endpoint para obtener provincias unicas (GET /api/provinces)
@api_bp.get("/provinces")
def get_provinces():
    # Consulta a la DB para obtener una lista de todas las provincias
    # únicas donde hay sitios visibles
    provinces = (
        db.session.query(distinct(Sitio.provincia))
        .filter(Sitio.visible == True)
        .order_by(Sitio.provincia)
        .all()
    )
    # Formatea la respuesta como una lista simple de strings
    data = [p[0] for p in provinces]
    
    return jsonify(data)


#endpoint para obtener todos los Tags (GET /api/tags)
@api_bp.get("/tags")
def get_all_tags():
    # Consulta a la DB para obtener todos los tags
    tags = db.session.query(Tag).order_by(Tag.nombre).all()
    
    # Formatea a la estructura {id, name}
    data = [{"id": t.id, "name": t.nombre} for t in tags]
    
    return jsonify(data)