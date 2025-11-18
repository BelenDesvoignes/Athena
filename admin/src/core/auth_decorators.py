from functools import wraps
from flask import request, jsonify, g, current_app
import jwt
from src.core.models.public_user import PublicUser
from src.core.database import db

def login_required_public(f):
    """
    Decorador para proteger rutas de la API pública.
    Requiere que el usuario envíe un JWT válido en el encabezado Authorization (Bearer <token>).
    Si el token es válido, asigna el objeto public_user a g.public_user.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # leer el encabezado de autorización
        auth_header = request.headers.get('Authorization')

        #verificar formato y existencia
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Autenticación requerida. Falta o es incorrecto el token."}), 401

        token = auth_header.split(" ")[1]
        SECRET_KEY = current_app.config.get("JWT_SECRET_KEY")

        if not SECRET_KEY:
             current_app.logger.error("JWT_SECRET_KEY no está configurada en la aplicación.")
             return jsonify({"error": "Error de configuración interna."}), 500

        try:
            # decodificar el Token
            # current_app.config["JWT_SECRET_KEY"] debe tener la misma clave usada para codificar.
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")

            # buscar el usuario en la DB
            user = db.session.get(PublicUser, user_id)
            if not user:
                return jsonify({"error": "Usuario asociado al token no encontrado."}), 401

            # asignar el usuario al contexto global (g)
            g.public_user = user

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado. Inicie sesión nuevamente."}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": f"Token inválido: {e}"}), 401
        except Exception as e:
            current_app.logger.error(f"Error desconocido en autenticación: {e}")
            return jsonify({"error": "Error de autenticación desconocido."}), 401

        return f(*args, **kwargs)
    return decorated_function


def optional_login_public(f):
    """
    Decorador para rutas públicas (ej. listados, detalles).
    Intenta autenticar al usuario usando el JWT si está presente.
    Si el token es válido, asigna g.public_user.
    Si el token falta o es inválido/expirado, la ruta continúa normalmente
    y g.public_user será None.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Inicializa el usuario público como None por defecto
        g.public_user = None

        auth_header = request.headers.get('Authorization')

        # Si no hay encabezado o no es Bearer, no hacemos nada y continuamos
        if not auth_header or not auth_header.startswith('Bearer '):
            return f(*args, **kwargs)

        token = auth_header.split(" ")[1]
        SECRET_KEY = current_app.config.get("JWT_SECRET_KEY")

        try:
            #  Decodificar el Token
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")

            #  Buscar el usuario
            user = db.session.get(PublicUser, user_id)

            #  Asignar el usuario al contexto global si se encuentra
            if user:
                g.public_user = user

            # Si el usuario no se encuentra, g.public_user sigue siendo None

        except Exception:
            # Captura jwt.ExpiredSignatureError, jwt.InvalidTokenError, etc.
            # Si hay CUALQUIER error en la decodificación, tratamos la petición como anónima.
            g.public_user = None

        return f(*args, **kwargs)
    return decorated_function