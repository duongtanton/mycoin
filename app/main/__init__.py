import io
import json
from flask import Blueprint, render_template, send_file, request, jsonify, session, redirect
from app.core.blockchain import generate_wallet, verify_password

bp = Blueprint('main', __name__)

@bp.get('/')
def index():
    return render_template('index.html')

@bp.get('/sign-in')
def signIn():
    session.pop('wallet', None)
    return render_template('sign-in.html')

@bp.post('/sign-in')
def signInWithKey():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    json_data = json.load(file)
    if file:
        if (verify_password(json_data, request.form['password'])):
            session['wallet'] = json_data
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "Invalid password"}), 401
    return jsonify({"error": "File to load file"}), 500

@bp.get('/sign-up')
def signUp():
    session.pop('wallet', None)
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
    if 'wallet' not in session:
        return redirect('/sign-in')
    return render_template('history.html')

@bp.get('/wallet')
def wallet():
    if 'wallet' not in session:
        return redirect('/sign-in')
    return render_template('wallet.html', wallet=session['wallet'])
    