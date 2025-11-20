from flask import Blueprint, request, jsonify
from src.core.models import PublicUser
from src.core.database import db
from sqlalchemy import select
from flask_jwt_extended import create_access_token

public_users_bp = Blueprint("public_users", __name__, url_prefix="/api/public_users")



@public_users_bp.route("/login", methods=["POST", "OPTIONS"])
def login_or_create_user():

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
