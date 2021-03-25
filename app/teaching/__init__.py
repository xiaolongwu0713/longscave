from flask import Blueprint

bp = Blueprint('teaching', __name__)

from app.teaching import routes
