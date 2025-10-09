<<<<<<< HEAD
# Registro y Preservación de Sitios Históricos
=======
# Registro y Preservación de Sitios Históricos.

## Participantes
- Amarilla, Kevin Ezequiel  
- Desvoignes, Maria Belen  
- Godoy, Valentina  
- Rodriguez Ricon, Mauricio Fernando  
- Tabbita, Julian  

## Descripción del proyecto
Aplicación web para documentar y gestionar sitios históricos de distintas ciudades del país. Permite:  
- Registro y administración de sitios históricos (información, ubicación, estado de conservación).  
- Gestión de usuarios, roles y permisos.  
- Validación de propuestas y reseñas de usuarios públicos.  
- Exportación de datos y trazabilidad de cambios.  

**Usuarios:**  
- Públicos: consultar sitios, dejar reseñas, proponer nuevos sitios.  
- Editores: administrar sitios, validar información y reseñas.  
- Administradores: todo lo de editores + gestión de usuarios y roles.  
- System Admin: acceso completo a todas las funcionalidades.  

## Tecnologías
- Backend: Python 3.12.3, Flask, SQLAlchemy, Flask-Session  
- Frontend privado: Jinja2 + Bootstrap   
- Base de datos: PostgreSQL 16 (soporte geoespacial)  
- Gestión de dependencias: Poetry 2.1.4  

## Instalación y ejecución

1. Clonar repositorio:  
```bash
git clone https://gitlab.catedras.linti.unlp.edu.ar/proyecto-2025/proyectos/grupo19/code.git
cd code

2. Instalar dependencias:
poetry install

3. Ejecutar la aplicación:
cd admin
poetry run flask --app main.py run
```

## Usuarios disponibles

Administrador
    E-Mail: admin@example.com
    Contraseña: admin123

Editor
    E-Mail: usuarioEditor@gmail.com
    Contraseña: editor123

Usuario publico
    E-Mail: usuarioPublico@gmail.com
    Contraseña: publico123