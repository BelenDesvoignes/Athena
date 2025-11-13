# Este archivo define cómo interactúa la app con la base de datos

from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy



class Base(DeclarativeBase):
    """
    Clase base declarativa para los modelos de SQLAlchemy.

    Esta clase sirve como el punto de partida para definir todos los modelos de la
    aplicación. Al heredar de ella, los modelos obtienen automáticamente la
    funcionalidad de mapeo objeto-relacional necesaria.
    """

    pass


db = SQLAlchemy(model_class=Base)




def init_db(app):
    """
    Inicializa la extensión de SQLAlchemy con la aplicación Flask.

    Args:
        app: Una instancia de la aplicación Flask.

    Returns:
        SQLAlchemy: La instancia de la base de datos inicializada.
    """
    # inicializa la aplicación con la instancia de db
    db.init_app(app)
    
    return db


def reset_db():
    print("Reseteando base de datos...")
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)
    print("Hecho!")
