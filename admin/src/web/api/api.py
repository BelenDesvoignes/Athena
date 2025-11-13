
from sqlalchemy import func
from src.core.models.review import Review, ReviewStatus
from flask import Blueprint, jsonify, request
from sqlalchemy import or_, func, desc, asc, distinct
from src.core.database import db
from src.core.models.site import Sitio
from src.core.models.tag import Tag
from src.core.models.tag import sitios_tags
from src.core.models.review import Review 
from src.core.api_validations import validate_api_params, SiteListParams 


api_bp = Blueprint("api_public", __name__, url_prefix="/api")

def get_sort_column(order_by_param):

    if order_by_param == 'nombre': return Sitio.nombre
    if order_by_param == 'registrado': return Sitio.registrado
    # 'calificacion' se maneja como el alias avg_rating
    return None

# Endpoint de prueba para sitios
@api_bp.get("/sites")
@validate_api_params(SiteListParams)
def get_sites(validated_params):

    #se usan los parametros validados 
    page = validated_params.page
    per_page = validated_params.per_page
    order_by = validated_params.order_by
    order_direction = validated_params.order
    search_term = validated_params.search
    ciudad = validated_params.city
    provincia = validated_params.province
    estado = validated_params.state
    tags_param = validated_params.tags

    #calculo de calificacion promedio solo resenas aprobadas 
    # coalesce(expr, 0) asegura que sitios sin reseñas tengan rating 0, no NULL.
    avg_rating = func.coalesce(
        func.avg(Review.rating).filter(Review.status == 'APROBADA'), 
        0
    ).label('calificacion_promedio')

    # Query base: Selecciona el Sitio y el promedio calculado.
    query = db.session.query(Sitio, avg_rating).filter(Sitio.visible == True)
    
    # LEFT JOIN para incluir sitios que NO tienen reseñas
    # y luego agrupamos por Sitio para calcular el promedio por ID.
    query = query.outerjoin(Review, Sitio.id == Review.site_id).group_by(Sitio.id)


    # busqueda por texto (aplica sobre nombre y descripcion breve)
    if search_term:
        search_like = f"%{search_term}%"
        # 'or_' para buscar el termino en cualquiera de los dos campos
        query = query.filter(or_(
            Sitio.nombre.ilike(search_like),
            Sitio.descripcion_breve.ilike(search_like)
        ))

    #filtros
    if ciudad:
        query = query.filter(Sitio.ciudad.ilike(f"%{ciudad}%"))
    if provincia:
        query = query.filter(Sitio.provincia == provincia)
    if estado:
        query = query.filter(Sitio.estado_conservacion == estado)        
   
    #tags 
    if tags_param:
        tag_ids = tags_param 
        if tag_ids:
            subquery = db.session.query(sitios_tags.c.sitio_id).filter(
                sitios_tags.c.tag_id.in_(tag_ids)
            ).group_by(sitios_tags.c.sitio_id).having(
                func.count(sitios_tags.c.tag_id) == len(tag_ids)
            ).subquery()
            query = query.filter(Sitio.id.in_(subquery)) 
           
    # ordenamiento 
    sort_column = None
    if order_by == 'nombre':
        sort_column = Sitio.nombre
    elif order_by == 'registrado':
        sort_column = Sitio.registrado
    elif order_by == 'calificacion':
        sort_column = avg_rating

    # Aplicar la dirección del orden
    if sort_column is not None:
        if order_direction == 'asc':
            query = query.order_by(asc(sort_column))
        else: # 'desc' o cualquier otro valor por defecto
            query = query.order_by(desc(sort_column))


    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    data = []
    for sitio, promedio_rating in pagination.items:
        data.append({
            "id": sitio.id,
            "name": sitio.nombre,
            "short_description": sitio.descripcion_breve,
            "city": sitio.ciudad,
            "province": sitio.provincia,
            "state_of_conservation": sitio.estado_conservacion,
            "registered_date": sitio.registrado.strftime('%Y-%m-%d'),
            "average_rating": round(promedio_rating, 2),
            # Incluir tags asociados (mostrar 5 máximo, como pide la consigna)
            "tags": [{"id": t.id, "name": t.nombre} for t in sitio.tags[:5]], 
            "image_url": "/img/default.jpg", # URL de imagen de portada (placeholder)
        })
    

    return jsonify({
        "data": data,
        "total": pagination.total,
        "pages": pagination.pages,
        "page": pagination.page,
        "per_page": pagination.per_page,})


@api_bp.get("/sites/<int:site_id>")
def get_site_detail(site_id):
    # Buscar el sitio visible por ID
    sitio = db.session.query(Sitio).filter_by(id=site_id, visible=True).first()

    if not sitio:
        return jsonify({"error": "Sitio no encontrado"}), 404

    # Calcular promedio de reseñas aprobadas
    promedio = (
        db.session.query(func.avg(Review.rating))
        .filter(Review.site_id == sitio.id, Review.status == 'APROBADA')
        .scalar()
    )
    promedio = round(promedio, 2) if promedio else 0

    # Devolver los datos del sitio
    data = {
        "id": sitio.id,
        "name": sitio.nombre,
        "description": sitio.descripcion_completa,
        "short_description": sitio.descripcion_breve,
        "city": sitio.ciudad,
        "province": sitio.provincia,
        "state_of_conservation": sitio.estado_conservacion,
        "registered_date": sitio.registrado.strftime('%Y-%m-%d'),
        "average_rating": promedio,
        "tags": [{"id": t.id, "name": t.nombre} for t in sitio.tags],
        "image_url": "/img/default.jpg",  # default por ahora
    }

    return jsonify(data)



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
