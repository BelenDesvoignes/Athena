from flask import Blueprint, request, jsonify
from src.core.models import PublicUser
from src.core.database import db
from sqlalchemy import select
from flask_jwt_extended import create_access_token

public_users_bp = Blueprint("public_users", __name__, url_prefix="/api/public_users")



@public_users_bp.route("/login", methods=["POST", "OPTIONS"])
def login_or_create_user():
    """
    Crea o inicia sesión de un usuario público según el email recibido.

    Métodos:
        - OPTIONS: Respuesta vacía para preflight CORS.
        - POST: Procesa el login o creación del usuario.

    Datos JSON esperados:
        - email (str): Email del usuario (obligatorio).
        - name (str): Nombre del usuario (opcional).

    Lógica:
        - Si el email no existe en la base, se crea un nuevo PublicUser.
        - Si ya existe, simplemente se devuelve el usuario.

    Respuestas:
        - 201: Usuario creado.
        - 200: Usuario existente.
        - 400: Falta el campo 'email'.

    Retorna:
        JSON con los datos del usuario y mensaje correspondiente.
    """
    
    
    if request.method == "OPTIONS":
        return "", 200

    
    data = request.get_json()
    print("💾 Datos recibidos:", data)
    email = data.get("email")
    name = data.get("name")

    if not email:
        return jsonify({"error": "Falta el campo 'email'"}), 400

    
   
    stmt = select(PublicUser).where(PublicUser.email == email)
    

    user = db.session.execute(stmt).scalar_one_or_none()

    
    if not user:
        user = PublicUser(email=email, name=name)
        db.session.add(user)
        db.session.commit()
        status_code = 201
        message = "Usuario creado correctamente"
    else:
        status_code = 200
        message = "Usuario existente"

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": message,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        },
        "access_token": access_token
    }), status_code


@public_users_bp.route("/", methods=["GET"])
def list_public_users():
    """
    Lista todos los usuarios públicos registrados.

    Método:
        - GET

    Retorna:
        - 200: Lista JSON de usuarios con id, email y name.
    """
    users = PublicUser.query.all()
    return jsonify([
        {"id": u.id, "email": u.email, "name": u.name}
        for u in users
    ]), 200


@public_users_bp.route("/<int:user_id>", methods=["GET"])
def get_public_user(user_id):
    """
    Obtiene la información de un usuario público por ID.

    Parámetros:
        - user_id (int): ID del usuario.

    Respuestas:
        - 200: JSON con los datos del usuario.
        - 404: Si no existe un usuario con ese ID.
    """
    user = PublicUser.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name
    }), 200
