from src.web import create_app
from src.core.database import db, reset_db
from src.core.seeds import seed_roles_permissions, seed_admin_user, seed_feature_flags,seed_sitios

    

app = create_app()



if __name__ == "__main__":
    app.run(debug=True)
