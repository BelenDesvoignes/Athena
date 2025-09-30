#Grupo19 

Participantes:

Amarilla, Kevin Ezequiel.
Desvoignes, Maria Belen.
Godoy, Valentina.
Rodriguez Ricon, Mauricio Fernando.
Tabbita, Julian.


## Problemas encontrados

1. Tenian mas de un pyproject.toml, uno en la raiz y otro adentro de src. Debe existir solo uno.
2. En poetry no estaba declarada como dependencia la libreria flask_sqlalchemy
3. En poetry no estaba declarada como dependencia flask_session

RECORDATORIO: las dependencias que utiliza el proyecto deben agregarse con poetry add NOMBRE_DEPENDENCIA

4. No estaba bien declarado el main.py para la ejecución via poetry.


Para encender el sistema

1. Poetry add install
2. poetry run flask --app main.py run (momentaneo)

