🏛️ Athena: Sistema de Gestión de Patrimonio Histórico
Athena es una solución web integral diseñada para la gestión, visualización y difusión del patrimonio histórico. Este proyecto fue desarrollado de forma colaborativa en el marco de la carrera de Sistemas en la UNLP.

El sistema permite a administradores gestionar sitios de interés cultural, mientras que el público general puede explorar el patrimonio mediante búsquedas geoespaciales y dejar reseñas.

🌐 Despliegue 
El proyecto se encuentra operativo en los siguientes enlaces:

Portal Público: https://grupo19.proyecto2025.linti.unlp.edu.ar/ 

Panel de Administración: https://admin-grupo19.proyecto2025.linti.unlp.edu.ar/

💻 Stack Tecnológico
Backend: Python 3.12 (Flask), SQLAlchemy (ORM).

Frontend: JavaScript (Vue.js 3), Vite, Bootstrap 5.

Base de Datos: PostgreSQL 16 con PostGIS para análisis de datos geoespaciales.

Infraestructura: Docker & Docker Compose, MinIO (Almacenamiento S3).

Seguridad: Google OAuth 2.0, Bcrypt para hashing de contraseñas.

🎯 Funcionalidades Principales
Panel de Administración
Gestión Integral (CRUD): Control total sobre sitios históricos y archivos multimedia.

Seguridad y Roles: Sistema de permisos, auditoría de acciones y autenticación robusta.

Análisis de Datos: Exportación de reportes en formato CSV.

Portal Público
Búsqueda Geoespacial: Localización de sitios mediante mapas interactivos (PostGIS).

Interacción Social: Sistema de reseñas, calificaciones y gestión de favoritos.

Experiencia de Usuario: Interfaz responsiva y autenticación con Google.

📁 Estructura del Repositorio
El código fuente se encuentra organizado de la siguiente manera:

/code/admin: Servidor Flask, modelos de datos y lógica de negocio.

/code/portal: Interfaz de usuario desarrollada en Vue.js.

🛠️ Instalación Rápida
Clonar el repositorio: git clone <url-repo>

Configurar variables: Crear archivos .env en /admin y /portal (ver ejemplos en el código).

Levantar infraestructura: cd code/admin && docker-compose up -d

Inicializar DB: flask reset-db && flask seed-db

👥 Créditos y Colaboración
Proyecto desarrollado colaborativamente por:

María Belén Desvoignes 
Valentina Godoy 
