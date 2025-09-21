from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

db = SQLAlchemy()

def init_db(app):
     """
    Inicializa la extensión de SQLAlchemy con la aplicación Flask.
    Args:
        app: Una instancia de la aplicación Flask.

    Returns:
        SQLAlchemy: La instancia de la base de datos inicializada.
    """
    db.init_app(app)
    return db


def Base (DeclarativeBase): 
    """
    Clase base declarativa para los modelos de SQLAlchemy.

    Esta clase sirve como el punto de partida para definir todos los modelos de la
    aplicación. Al heredar de ella, los modelos obtienen automáticamente la
    funcionalidad de mapeo objeto-relacional necesaria.
    """
    pass    

