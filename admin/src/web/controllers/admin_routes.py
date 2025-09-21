from flask import Blueprint, render_template



#crea instancia del blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='../templates')



#define la ruta de la pagina de inicio del admin 
@admin_bp.route('/')
def home():
    return render_template('home.html')