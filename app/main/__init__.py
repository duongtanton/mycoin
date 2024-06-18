from flask import Blueprint
from flask import render_template

bp = Blueprint('main', __name__)

@bp.get('/')
def index():
    return render_template('index.html')

@bp.get('/sign-in')
def signIn():
    return render_template('sign-in.html')

@bp.get('/sign-up')
def signUp():
    return render_template('sign-up.html')

@bp.get('/history')
def history():
    return render_template('history.html')