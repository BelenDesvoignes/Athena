from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from src.core.bcrypt import check_password
from src.web.api.api import api_bp
from src.core.models.user import User
from src.core.database import db 

@api_bp.post("/auth", endpoint="login")
def login():
    """
    Gestiona la autenticación de un usuario mediante email y contraseña.

    Verifica las credenciales proporcionadas. Si son válidas, genera un token
    de acceso JWT (JSON Web Token) para el usuario autenticado.

    Args:
        None: La función espera recibir los datos de autenticación a través
              del cuerpo de la solicitud JSON (request body).

    Request JSON Body:
        email (str): El correo electrónico del usuario.
        password (str): La contraseña en texto plano.

    Returns:
        tuple: Una tupla que contiene el objeto JSON de respuesta y el código de estado HTTP.
               - 200 OK: Autenticación exitosa. Retorna el token de acceso y su tiempo de expiración.
               - 401 Unauthorized: Usuario o contraseña incorrectos.

        JSON on 200 OK:
            token (str): El token de acceso JWT.
            expires_in (int): Tiempo de vida del token en segundos (ej: 3600 segundos = 1 hora).
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    query = db.session.query(User).filter(User.email == email)
    user = query.first()

    if not user or not check_password(password, user.password):
        return jsonify({"msg": "Usuario o contraseña incorrectos"}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": access_token,
        "expires_in": 3600
    }), 200
