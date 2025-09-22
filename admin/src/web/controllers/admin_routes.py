from flask import Blueprint, render_template, request, redirect, url_for, session
from src.core.user_service import get_user_by_email, create_user

# Crea una instancia del blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='../templates')

# Ruta de Login
# Esta ruta manejará la URL /admin/
@admin_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = get_user_by_email(email)
        
        if user and user.check_password(password):
            # Autenticación exitosa
            session['user_id'] = user.id
            session['user_role'] = user.rol
            
            # Redirige a la página de inicio (home.html)
            return redirect(url_for('admin.home'))
        else:
            # Autenticación fallida
            return render_template('login.html', error="Credenciales inválidas o cuenta inactiva.")

    return render_template('login.html')

# Define la ruta de la página de inicio del admin (probablemente para un dashboard)
# Esta ruta manejará la URL /admin/home
@admin_bp.route('/home')
def home():
    # En un escenario real, esta ruta debería estar protegida
    return render_template('home.html')

# Ruta de Registro
@admin_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Obtener los datos del formulario
        data = {
            'nombre': request.form['nombre'],
            'apellido': request.form['apellido'],
            'email': request.form['email'],
            'password': request.form['password'],
            'rol': 'Usuario público',
            'activo': True
        }
        
        # Llama a la función de servicio para crear el usuario
        new_user = create_user(data)
        
        if new_user:
            return redirect(url_for('admin.login'))
        else:
            return render_template('register.html', error="El email ya está registrado.")
    
    return render_template('register.html')



#/admin/home  muestra pagina principal 
#/admin muestra el login 
#admin/register muestra el registro 