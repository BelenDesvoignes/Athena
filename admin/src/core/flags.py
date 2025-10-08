from src.core.database import db
from src.core.models.feature_flags import FeatureFlag
import logging

logging.basicConfig(level=logging.DEBUG)

def get_flag_by_name(flag_name: str) -> FeatureFlag:
    """
    Obtiene un FeatureFlag por su clave.

    Args:
        flag_name (str): Nombre del flag a buscar.

    Returns:
        FeatureFlag: Objeto del flag encontrado.
    """
    flag = (
        db.session.execute(
            db.select(FeatureFlag).filter_by(key=flag_name)
        )
        .unique()
        .scalar_one_or_none()
    )

    if not flag:
        raise ValueError(f"El flag '{flag_name}' no existe en la base de datos.")
    
    logging.debug(f"Flag encontrado: {flag}")
    return flag

def is_flag_enabled(flag_name: str) -> bool:
    """
    Verifica si un FeatureFlag está habilitado.

    Args:
        flag_name (str): Nombre del flag a verificar.

    Returns:
        bool: True si está habilitado, False en caso contrario o si no existe.
    """
    try:
        flag = get_flag_by_name(flag_name)
        logging.debug(f"Flag '{flag_name}' está {'ON' if flag.is_enabled else 'OFF'}")
        return flag.is_enabled
    except ValueError:
        logging.warning(f"Flag '{flag_name}' no encontrado, se considera OFF por defecto.")
        return False

