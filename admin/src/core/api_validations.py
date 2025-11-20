from dataclasses import dataclass, field
from typing import Optional, List
from flask import request, jsonify

# constantes y Listas de valores permitidos
ALLOWED_ORDER_BY = ['registrado', 'nombre', 'calificacion', 'distancia']
ALLOWED_ORDER_DIRECTION = ['asc', 'desc']
ALLOWED_STATES = ['EXCELENTE', 'BUENO', 'REGULAR', 'MALO']
MAX_PER_PAGE = 50 # limite max para la paginacion

# decorador de validacion
def validate_api_params(dataclass_model):
    """
    Decorador que toma los query parameters de la solicitud de Flask,
    los valida con el modelo dataclass y pasa los parámetros limpios a la función.
    Retorna 400 Bad Request si la validación falla.
    """
    def wrapper(func):
        def inner(*args, **kwargs):
            try:
                # crea el objeto con los datos de la solicitud (esto llama a __post_init__)
                validated_params = dataclass_model.from_request(request)

                # pasa los parámetros validados (objeto) a la función de la ruta
                kwargs['validated_params'] = validated_params
                return func(*args, **kwargs)

            except ValueError as e:
                # captura el error de validación y retorna 400
                return jsonify({"error": str(e)}), 400
        return inner
    return wrapper

# modelo de parametros de busqueda y listado sitios
@dataclass
class SiteListParams:
    # definicion de tipos de datos y valores por defecto
    page: int = 1
    per_page: int = 10
    order_by: str = 'registrado'
    order: str = 'desc'
    search: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    tags: Optional[List[int]] = field(default_factory=list)
    lat: Optional[float] = None
    lon: Optional[float] = None
    radius: Optional[float] = None # radio en km

    is_favorite: bool = False

    # conversion de string de la URL a tipos de Python
    @classmethod
    def from_request(cls, req):
        args = req.args

        # Manejo de 'tags': Convierte el string '1,2,3' a lista de enteros [1, 2, 3]
        tags_list = []
        tags_str = args.get('tags')
        if tags_str:
            try:
                tags_list = [int(t.strip()) for t in tags_str.split(',') if t.strip()]
            except ValueError:
                raise ValueError("El parámetro 'tags' debe ser una lista de IDs numéricos separados por coma.")

        # Función auxiliar para parsear float o None
        def parse_float(param_name):
            value = args.get(param_name)
            if value is None or value == "":
                return None
            try:
                return float(value)
            except ValueError:
                raise ValueError(f"El parámetro '{param_name}' debe ser un flotante valido")

        # Función auxiliar para parsear booleano o usar valor por defecto False
        def parse_bool(param_name, default=False):
            value = args.get(param_name, '').lower()
            if value in ('true', '1'):
                return True
            return default


        try:
            # Recolectar parametros y convertirlos al tipo correcto (entero para page/per_page)
            # CORRECCIÓN: Usar str() con el valor por defecto para asegurar que .strip() siempre se aplique a una cadena.
            return cls(
                page=int(str(args.get('page', 1)).strip()),         # <--- CORRECCIÓN APLICADA
                per_page=int(str(args.get('per_page', 10)).strip()), # <--- CORRECCIÓN APLICADA
                order_by=args.get('order_by', 'registrado').strip(),
                order=args.get('order', 'desc').strip(),
                search=args.get('search'),
                province=args.get('province'),
                city=args.get('city'),
                state=args.get('state'),
                tags=tags_list,
                lat=parse_float('lat'),
                lon=parse_float('lon'),
                radius=parse_float('radius'),
                is_favorite=parse_bool('is_favorite')
            )
        except ValueError as e:
            # Propaga el error específico de parse_float o el error genérico de int
            if "flotante válido" in str(e):
                raise e
            raise ValueError("Los parámetros de paginación o enteros no son válidos.")


    # logica de validacion (se ejecuta automaticamente al crear la instancia)
    def __post_init__(self):
        # validacion de paginacion
        if self.page < 1:
            raise ValueError("El número de página (page) debe ser mayor o igual a 1.")
        if self.per_page < 1 or self.per_page > MAX_PER_PAGE:
            raise ValueError(f"El número de elementos por página (per_page) debe estar entre 1 y {MAX_PER_PAGE}.")

        # validacion de geolocalizacion
        # parametros numericos (solo si existen)
        if self.lat is not None and (self.lat < -90 or self.lat > 90):
            raise ValueError("La latitud ('lat') debe estar entre -90 y 90.")
        if self.lon is not None and (self.lon < -180 or self.lon > 180):
            raise ValueError("La longitud ('lon') debe estar entre -180 y 180.")
        if self.radius is not None and self.radius <= 0:
            raise ValueError("El radio ('radius') debe ser un valor positivo en km.")

        # validacion de consistencia: si se usa un parámetro geo, deben estar los 3 (lat, lon, radius)
        geo_params = [self.lat, self.lon, self.radius]
        if any(p is not None for p in geo_params) and not all(p is not None for p in geo_params):
            raise ValueError("Para la búsqueda por proximidad, los parámetros 'lat', 'lon' y 'radius' deben proporcionarse juntos.")

        # ordena por 'distancia' solo si los parámetros geo están presentes
        is_geo_filter_active = all(p is not None for p in geo_params)

        # validacion de ordenamiento
        if self.order_by not in ALLOWED_ORDER_BY:
            raise ValueError(f"El campo de ordenamiento '{self.order_by}' no es válido. Opciones: {', '.join(ALLOWED_ORDER_BY)}.")
        if self.order_by == 'distancia' and not is_geo_filter_active:
            raise ValueError("No se puede ordenar por 'distancia' sin proporcionar los parámetros 'lat', 'lon' y 'radius'.")
        if self.order not in ALLOWED_ORDER_DIRECTION:
            raise ValueError(f"La dirección de ordenamiento '{self.order}' no es válida. Opciones: {', '.join(ALLOWED_ORDER_DIRECTION)}.")

        # validacion y normalizacion de estado
        if self.state:
            normalized_state = self.state.upper()
            if normalized_state not in ALLOWED_STATES:
                raise ValueError(f"El estado de conservación '{self.state}' no es válido. Opciones: {', '.join(ALLOWED_STATES)}.")
            # Normalizar el estado guardado para que se use el capitalizado en la lógica del negocio
            self.state = self.state.capitalize()

        # limpiar cadenas de texto
        if self.search: self.search = self.search.strip()
        if self.province: self.province = self.province.strip()
        if self.city: self.city = self.city.strip()