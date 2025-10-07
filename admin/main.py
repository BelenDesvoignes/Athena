from src.web import create_app
from src.core.database import db
from src.core.seeds import seed_roles_permissions, seed_admin_user 

app = create_app()

with app.app_context():
    print("Iniciando creación de tablas y siembra de datos...")
    db.create_all()
    seed_roles_permissions() 
    seed_admin_user()        
    
    print("Tablas y datos iniciales listos.")

if __name__ == "__main__":
    app.run(debug=True)
