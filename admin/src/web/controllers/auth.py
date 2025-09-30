# controlador de autenticacion
# funcion: manejar formulario de login, procesar la autenticacion
# de credenciales, gestionar cierre de sesion
# sujeto a modificaciones
# src/web/controllers/auth.py
from src.core.models.role_permission import Role
from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from src.core.user_service import authenticate_user, create_user
from src.core.permissions_service import get_role_by_name
from src.web.handlers.auth import login_required 

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route("/", methods=['GET'])
def login():
    if 'user_id' in session:
        return redirect(url_for("admin.home"))
    return render_template("login.html")

@auth_bp.route("/authenticate", methods=['POST'])
def authenticate():
    email = request.form.get("email")
    password = request.form.get("password")

    user = authenticate_user(email, password)
    
    if not user:
        flash("Usuario o contraseña incorrecta.", "danger") 
        return redirect(url_for("auth.login")) 


    # Creación de la sesión
    #los datos del usuario se almacenan en el diccionario de la sesion
    session['user_id'] = user.id
    session['email'] = user.email
    session['nombre'] = f"{user.nombre}" 
    session['rol'] = user.rol
    
    flash(f"Bienvenido, {user.nombre}.", "success")
    return redirect(url_for("admin.home")) 



#ruta de registro
@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for("admin.home"))
        
    if request.method == 'POST':
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        email = request.form.get("email")
        password = request.form.get("password")
        role_obj = get_role_by_name("Usuario público") 
        role_id = role_obj.id 
        print(role_id)
        try:
            # Chequeo de que el email no exista y creación del usuario.
            # La función create_user se encarga de hashear la contraseña.
            create_user({
                "nombre": nombre,
                "apellido": apellido,
                "email": email,
                "password": password,
                "role_id": role_id, # Asignación de rol por defecto
                "enabled": True
            })
            
            flash("Registro exitoso. ¡Inicia sesión!", "success")
            return redirect(url_for("auth.login"))

        except ValueError as e:
            # Captura errores como 'Email ya registrado' o validaciones internas
            flash(str(e), "danger") 
            return render_template("register.html")
        except Exception:
            flash("Ocurrió un error al intentar registrar el usuario.", "danger")
            return render_template("register.html")

    return render_template("register.html")


@auth_bp.route("/logout")
@login_required 
def logout():
    #clear elimina los datos del servidor
    session.clear() 
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for("auth.login"))