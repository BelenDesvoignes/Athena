from flask import Blueprint, request, jsonify, current_app
from src.core.models import PublicUser
from src.core.database import db
from sqlalchemy import select
import jwt
from datetime import datetime, timedelta, timezone

public_users_bp = Blueprint("public_users", __name__, url_prefix="/api/public_users")



@public_users_bp.route("/login", methods=["POST", "OPTIONS"])
def login_or_create_user():

    # Manejar explícitamente la petición OPTIONS (pre-vuelo)
    if request.method == "OPTIONS":
        return "", 200

    # Lógica POST
    data = request.get_json()
    print("💾 Datos recibidos:", data)
    email = data.get("email")
    name = data.get("name")

    if not email:
        return jsonify({"error": "Falta el campo 'email'"}), 400


    # Construir la consulta de selección
    stmt = select(PublicUser).where(PublicUser.email == email)

    # Ejecutar la consulta y obtener el primer resultado
    user = db.session.execute(stmt).scalar_one_or_none() # ⬅️ CLAVE

    # Si no existe, crear uno nuevo
    if not user:
        user = PublicUser(email=email, name=name)
        db.session.add(user)
        db.session.commit()
        status_code = 201
        message = "Usuario creado correctamente"
    else:
        status_code = 200
        message = "Usuario existente"

    #logica de generacion jwt
    #  expiracion 24 horas
    expiration_time = datetime.now(timezone.utc) + timedelta(hours=24)

    payload = {
        "user_id": user.id,
        "exp": expiration_time, # Expiration Time
        "iat": datetime.now(timezone.utc) # Issued At (Momento de creación)
    }

    #obtengo la clave secreta de la configuración de Flask
    secret_key = current_app.config.get("JWT_SECRET_KEY")

    if not secret_key:
         return jsonify({"error": "Error de configuración: JWT_SECRET_KEY no definida."}), 500

    # codificar el token
    token = jwt.encode(
        payload,
        secret_key,
        algorithm="HS256"
    )

    # devolver el token en la respuesta
    return jsonify({
        "message": message,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        },
        "token": token #token de acceso
    }), status_code

@public_users_bp.route("/", methods=["GET"])
def list_public_users():
    users = PublicUser.query.all()
    return jsonify([
        {"id": u.id, "email": u.email, "name": u.name}
        for u in users
    ]), 200


@public_users_bp.route("/<int:user_id>", methods=["GET"])
def get_public_user(user_id):
    user = PublicUser.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name
    }), 200
