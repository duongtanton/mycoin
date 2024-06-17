from flask import Blueprint
from flask import render_template

bp = Blueprint('auth', __name__)

@bp.get('/')
def index():
    return render_template('index.html', title='Home')