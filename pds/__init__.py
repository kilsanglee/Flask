from flask import Blueprint

pds_bp = Blueprint('pds_bp'
                     ,__name__
                     ,template_folder='templates')

from . import routes
