from flask import Blueprint

bp = Blueprint('alipay', __name__)

from app.alipay import routes
