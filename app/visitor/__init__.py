from flask import Blueprint

bp = Blueprint('visitor', __name__)

from app.visitor import routes
