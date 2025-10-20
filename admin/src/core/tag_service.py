import re

from sqlalchemy import exists

from src.core.database import db
from src.core.models.tag import Tag, sitios_tags


def get_tag_by_slug(slug):
    """
    Obtiene una etiqueta (Tag) a partir de su slug.

    Args:
        slug (str): Slug único de la etiqueta.

    Returns:
        Tag | None: Objeto Tag si existe, de lo contrario None.
    """
    return db.session.query(Tag).filter_by(slug=slug).first()

def get_tag_by_id(tag_id):
    """
    Obtiene una etiqueta (Tag) por su ID.

    Args:
        tag_id (int): ID de la etiqueta.

    Returns:
        Tag | None: Objeto Tag si se encuentra, None si no existe.
    """
    return db.session.get(Tag, tag_id)

def get_tag_by_name(nombre):
    """
    Obtiene una etiqueta (Tag) a partir de su nombre,
    generando el slug correspondiente para la búsqueda.

    Args:
        nombre (str): Nombre de la etiqueta.

    Returns:
        Tag | None: Objeto Tag si existe, None si no.
    """
    slug = generate_slug(nombre)
    return db.session.query(Tag).filter_by(slug=slug).first()

def generate_slug(nombre):
    """
    Genera un slug válido a partir del nombre de una etiqueta.

    Convierte el texto a minúsculas y reemplaza cualquier
    carácter no alfanumérico por guiones bajos.

    Args:
        nombre (str): Nombre original de la etiqueta.

    Returns:
        str: Slug generado.
    """
    nombre = nombre.lower()

    nombre = re.sub(r"[^a-z0-9]+", "_", nombre)

    return nombre

def create_tag(data):
    """
    Crea una nueva etiqueta en la base de datos.

    Args:
        data (dict): Diccionario con los datos del nuevo Tag.
            Ejemplo: {"nombre": "Ejemplo", "slug": "ejemplo"}

    Returns:
        Tag: Objeto Tag recién creado.
    """
    new_tag = Tag(**data)
    db.session.add(new_tag)
    db.session.commit()
    return new_tag

def update_tag(tag_id, nombre):
    """
    Actualiza el nombre y el slug de una etiqueta existente.

    Args:
        tag_id (int): ID de la etiqueta a actualizar.
        nombre (str): Nuevo nombre de la etiqueta.

    Returns:
        Tag | None: Objeto Tag actualizado o None si no se encontró.
    """
    tag = get_tag_by_id(tag_id)
    if tag:
        setattr(tag, 'nombre', nombre)
        setattr(tag, 'slug', generate_slug(nombre))
    db.session.commit()
    return tag

def delete_tag(tag_id):
    """
    Elimina una etiqueta por su ID.

    Args:
        tag_id (int): ID de la etiqueta a eliminar.

    Returns:
        bool: True si la etiqueta fue eliminada, False si no existía.
    """
    tag = get_tag_by_id(tag_id)
    if tag:
        db.session.delete(tag)
        db.session.commit()
        return True
    return False

def list_tags(page, per_page, busqueda=None, order_by=None, order_dir=None):
    """
    Lista etiquetas con soporte de paginación, búsqueda y ordenamiento.

    Args:
        page (int): Número de página actual.
        per_page (int): Cantidad de resultados por página.
        busqueda (str, optional): Texto para filtrar por nombre. Default: None.
        order_by (str, optional): Campo por el cual ordenar. Default: None.
        order_dir (str, optional): Dirección de orden ('asc' o 'desc'). Default: None.

    Returns:
        Pagination: Objeto con los resultados paginados.
    """

    query = db.session.query(Tag)

    if busqueda:
        query = query.filter(Tag.nombre.ilike(f"%{busqueda}%"))
        
    if hasattr(Tag, order_by):
        column = getattr(Tag, order_by)
        if order_dir == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

    
    total = query.count()
    tags = query.offset((page - 1) * per_page).limit(per_page).all()

  
    class Pagination:
        """Clase auxiliar para representar resultados paginados."""
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page

    return Pagination(tags, page, per_page, total)

def used_tag(tag_id):
    """
    Verifica si una etiqueta está siendo utilizada en alguna relación.

    Args:
        tag_id (int): ID de la etiqueta a verificar.

    Returns:
        bool: True si la etiqueta está asociada a algún sitio, False en caso contrario.
    """

    usado = db.session.query(exists().where(sitios_tags.c.tag_id == tag_id)).scalar()

    return usado