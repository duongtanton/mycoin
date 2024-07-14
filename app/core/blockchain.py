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
import random

blockChain = None            

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = time.time()
        self.id = time.time()
        
    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "id": self.id
        }

class Block:
    def __init__(self, data:list[Transaction]):
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
            total += int(transaction.amount)
        return total
class TransactionEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Transaction):
            return obj.to_dict()
        return super().default(obj)

def hash(block):
    data = json.dumps(block.data, cls=TransactionEncoder) + block.prev_hash + str(block.none)
    data = data.encode("utf-8")
    return sha256(data).hexdigest()

def next_block(last_block, data):
    block = Block(data)
    block.prev_hash = last_block.hash
    block.hash = hash(block)
    return block
class Validator:
    def __init__(self, address, stake):
        self.address = address
        self.stake = stake
        
class BlockChain:
    def __init__(self):
        self.chain:list[Block] = []
        block = Block([])
        block.hash = hash(block)
        self.chain.append(block)
        self.temp_data:list[Transaction] = []
        self.validators = {}
        
    # def add_block(self, data):
    #     block = Block(data)
    #     block.prev_hash = self.chain[-1].hash
    #     while block.hash[:2] != "00":
    #         block.none += 1
    #         block.hash = hash(block)
    #     block.hash = hash(block)
    #     self.chain.append(block)   
    #     self.temp_data = [] 
    
    def add_block(self, validator_address):
        if validator_address in self.validators:
            last_block = self.chain[-1]
            new_block = next_block(last_block, self.temp_data)
            self.temp_data = []
            self.chain.append(new_block)
        else:
            print("Invalid validator")
            
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
                if transaction.sender == address:
                    balance -= int(transaction.amount)
                if transaction.receiver == address:
                    balance += int(transaction.amount)
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
                if transaction.sender == address or transaction.receiver == address or address == None:
                    transactions.insert(0, transaction)
        return transactions              
     
    def add_transaction(self, transaction):
        self.temp_data.append(transaction)

    def register_validator(self, address, stake):
        self.validators[address] = Validator(address, stake)

    def select_validator(self):
        total_stake = sum(validator.stake for validator in self.validators.values())
        pick = random.uniform(0, total_stake)
        current = 0
        for validator in self.validators.values():
            current += validator.stake
            if current > pick:
                return validator.address

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
    blockChain.register_validator("Validator1", 50)
    blockChain.register_validator("Validator2", 30)
    blockChain.register_validator("Validator3", 20)
    blockChain.add_transaction(Transaction("tonduong", "17qyQFhvqDurYVmqjWJMKTwBfQNWZx32B", 100))
    selected_validator = blockChain.select_validator()
    blockChain.add_block(selected_validator)
    while True:
        time.sleep(5)
        print("Checking for new transactions")
        if len(blockChain.temp_data) > 0:
            print("New transactions found")
            selected_validator = blockChain.select_validator()
            blockChain.add_block(selected_validator)
    
    
   