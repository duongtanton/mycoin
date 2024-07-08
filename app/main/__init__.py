import io
import json
from flask import Blueprint
from flask import render_template
from flask import send_file, request, jsonify
from app.core.blockchain import generate_wallet

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

@bp.post('/sign-up')
def signUpGenWallet():
    if request.is_json:
        genWallet = request.get_json()
        password = genWallet["password"]
        wallet =  generate_wallet(password)
        file = io.BytesIO()
        file.write(json.dumps(wallet).encode('utf-8'))
        file.seek(0)
        return send_file(file, as_attachment=True, download_name=wallet["address"])
    else:
        return jsonify({"error": "Request must be JSON"}), 400

@bp.get('/history')
def history():
    return render_template('history.html')

@bp.get('/wallet')
def wallet():
    return render_template('wallet.html')