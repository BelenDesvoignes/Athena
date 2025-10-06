from src.core.models.tag import Tag
from src.core.database import db
import re

def get_tag_by_slug(slug):
    return db.session.query(Tag).filter_by(slug=slug).first()

def get_tag_by_id(tag_id):
    return db.session.get(Tag, tag_id)

def get_tag_by_name(nombre):
    slug = generate_slug(nombre)
    return db.session.query(Tag).filter_by(slug=slug).first()

def generate_slug(nombre):
    #pongo todo en minusculas
    nombre = nombre.lower()

    #reemplazo espacios, puntos y demas en guiones
    nombre = re.sub(r"[^a-z0-9]+", "_", nombre)

    return nombre

def create_tag(data):
    new_tag = Tag(**data)
    db.session.add(new_tag)
    db.session.commit()
    return new_tag

def update_tag(tag_id, nombre):
    tag = get_tag_by_id(tag_id)
    if tag:
        setattr(tag, 'nombre', nombre)
        setattr(tag, 'slug', generate_slug(nombre))
    db.session.commit()
    return tag

def delete_tag(tag_id):
    tag = get_tag_by_id(tag_id)
    if tag:
        db.session.delete(tag)
        db.session.commit()
        return True
    return False

def list_tags(page, per_page, search_nombre=None, search_slug=None, order_by='fecha_creacion', order_dir='desc'):
    # Usamos SQLAlchemy puro
    query = db.session.query(Tag)

    if search_nombre:
        query = query.filter(Tag.nombre.ilike(f"%{search_nombre}%"))

    if search_slug:
        query = query.filter(Tag.slug.ilike(f"%{search_slug}%"))

    if hasattr(Tag, order_by):
        column = getattr(Tag, order_by)
        if order_dir == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

    
    total = query.count()
    tags = query.offset((page - 1) * per_page).limit(per_page).all()

  
    class Pagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page

    return Pagination(tags, page, per_page, total)