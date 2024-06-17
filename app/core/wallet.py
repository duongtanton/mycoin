import os
import ecdsa
import hashlib

class Wallet:
    def __init__(self):
        self.private_key = self.generate_private_key()
        self.public_key = self.generate_public_key(self.private_key)
        self.address = self.generate_address(self.public_key)
    
    def generate_private_key(self):
        return os.urandom(32).hex()
    
    def generate_public_key(self, private_key):
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        return vk.to_string().hex()
    
    def generate_address(self, public_key):
        public_key_bytes = bytes.fromhex(public_key)
        sha256_bpk = hashlib.sha256(public_key_bytes).digest()
        ripemd160_bpk = hashlib.new('ripemd160', sha256_bpk).digest()
        return ripemd160_bpk.hex()

    def get_balance(self):
        return self.balance

    def add_transaction_to_history(self, transaction):
        self.transaction_history.append(transaction)

    def __str__(self):
        return f"Wallet Address: {self.address}\nBalance: {self.balance}\n"