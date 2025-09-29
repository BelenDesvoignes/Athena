import bcrypt 
from typing import Union

def hash_password(password: str) -> bytes:
    """
    Genera un hash seguro para la contraseña usando bcrypt.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password: str, hashed_password: Union[bytes, str]) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con el hash almacenado.
    """
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
        
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)