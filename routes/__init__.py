from flask import Blueprint
routes = Blueprint('routes', __name__)

from .index import *
from .follow import *
from .home import *
from .images import *
from .group import *
from .tags import *