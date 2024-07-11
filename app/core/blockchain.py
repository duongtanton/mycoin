import os
import json
import base58
import hashlib
import ecdsa
import time
from hashlib import sha256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64

blockChain = None            

class Block:
    def __init__(self, data):
        self.data = data
        self.prev_hash = ""
        self.hash = ""
        self.none = 0
        self.timestamp = time.time()
        self.id = time.time()
        self.total_amount = self.get_total_amount()
    
    def get_total_amount(self):
        total = 0
        for transaction in self.data:
            total += transaction["amount"]
        return total

def hash(block):
    data = json.dumps(block.data) + block.prev_hash + str(block.none)
    data = data.encode("utf-8")
    return sha256(data).hexdigest()

class BlockChain:
    def __init__(self):
        self.chain = []
        block = Block([])
        block.hash = hash(block)
        self.chain.append(block)
        
    def add_block(self, data):
        block = Block(data)
        block.prev_hash = self.chain[-1].hash
        while block.hash[:2] != "00":
            block.none += 1
            block.hash = hash(block)
        block.hash = hash(block)
        self.chain.append(block)    

    def is_valid(self):
        for i in range(1, len(self.chain)):
            if self.chain[i].hash != hash(self.chain[i]):
                return False
            if self.chain[i].prev_hash != self.chain[i-1].hash:
                return False
        return True
    
    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for transaction in block.data:
                if transaction["sender"] == address:
                    balance -= transaction["amount"]
                if transaction["receiver"] == address:
                    balance += transaction["amount"]
        return balance
     
    def get_blocks(self):
        blocks = []
        for block in self.chain:
            blocks.insert(0, block)
        return blocks
    
    def get_transactions(self, address = None):
        transactions = []
        for block in self.chain:
            for transaction in block.data:
                if transaction["sender"] == address or transaction["receiver"] == address or address == None:
                    transactions.insert(0, transaction)
        return transactions              
                  
def generate_wallet(password):
    private_key = os.urandom(32)
    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()

    public_key = b'\04' + vk.to_string()

    sha256_bpk = hashlib.sha256(public_key).digest()
    ripemd160_bpk = hashlib.new('ripemd160', sha256_bpk).digest()

    network_byte = b'\x00'
    network_bpk = network_byte + ripemd160_bpk

    sha256_nbpk = hashlib.sha256(network_bpk).digest()
    sha256_2_nbpk = hashlib.sha256(sha256_nbpk).digest()

    checksum = sha256_2_nbpk[:4]

    address = base58.b58encode(network_bpk + checksum)

    # Generate a salt
    salt = os.urandom(16)

    # Derive a key from the password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())

    # Encrypt the private key with the derived key using AES-GCM
    iv = os.urandom(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_private_key = encryptor.update(private_key) + encryptor.finalize()
    tag = encryptor.tag

    wallet = {
        'address': address.decode(),
        'encrypted_private_key': base64.b64encode(encrypted_private_key).decode(),
        'salt': base64.b64encode(salt).decode(),
        'iv': base64.b64encode(iv).decode(),
        'tag': base64.b64encode(tag).decode()
    }

    return wallet
  
def verify_password(wallet, password):
    encrypted_private_key = base64.b64decode(wallet['encrypted_private_key'])
    salt = base64.b64decode(wallet['salt'])
    iv = base64.b64decode(wallet['iv'])
    tag = base64.b64decode(wallet['tag'])

    # Derive a key from the password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())

    # Decrypt the private key with the derived key using AES-GCM
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    try:
        private_key = decryptor.update(encrypted_private_key) + decryptor.finalize()
        return True
    except Exception as e:
        print(f"Error decrypting private key: {e}")
        return False
    
def init_blockchain():
    global blockChain
    blockChain = BlockChain()
    blockChain.add_block([{
        "id": time.time(),
        "sender": "tonduong", 
        "receiver": "17qyQFhvqDurYVmqjWJMKTwBfQNWZx32B", 
        "amount": 100,
        "timestamp": time.time()
    }])
   