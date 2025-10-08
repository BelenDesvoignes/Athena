from src.web import create_app
from src.core.database import db, reset_db
from src.core.seeds import seed_roles_permissions, seed_admin_user, seed_feature_flags,seed_sitios

    

app = create_app()

with app.app_context():

    print("Limpieza de base de datos")
    reset_db()

    print("Iniciando creación de tablas y siembra de datos...")
    db.create_all()
    seed_roles_permissions() 
    seed_admin_user()        
    seed_feature_flags()
    seed_sitios()
    print("Tablas y datos iniciales listos.")

if __name__ == "__main__":
    app.run(debug=True)
