import io
import json
from flask import Blueprint, render_template, send_file, request, jsonify, session, redirect
from app.core.blockchain import generate_wallet, verify_password, blockChain, Transaction

bp = Blueprint('main', __name__)

@bp.get('/')
def index():
    global blockChain
    transactions = blockChain.get_transactions()
    blocks = blockChain.get_blocks()
    return render_template('index.html', transactions=transactions, blocks=blocks)

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

@bp.get('/wallet')
def wallet():
    if 'wallet' not in session:
        return redirect('/sign-in')
    global blockChain
    wallet = session['wallet']
    transactions = blockChain.get_transactions(wallet["address"])
    balance = blockChain.get_balance(wallet["address"])
    return render_template('wallet.html', transactions=transactions, balance=balance)
    
@bp.post('/transfer')
def transfer():
    if 'wallet' not in session:
        return redirect('/sign-in')
    global blockChain
    wallet = session['wallet']
    if request.is_json:
        transaction = request.get_json()
        transaction = Transaction(wallet["address"], transaction["receiver"], int(transaction["amount"]))
        blockChain.add_transaction(transaction)
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400    