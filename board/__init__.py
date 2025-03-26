from flask import Blueprint

board_bp = Blueprint('board_bp'
                     ,__name__
                     ,template_folder='templates')

from . import routes
