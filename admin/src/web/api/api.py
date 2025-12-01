from flask import Blueprint

api_bp = Blueprint("api_public", __name__, url_prefix="/api")

from .api import *
from .minio import *
from .review_management import *
from .sites_provinces import *
from .login import *

