import time
import ecdsa

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = int(time.time())
        self.signature = None

    def sign_transaction(self, private_key):
        sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_key), curve=ecdsa.SECP256k1)
        message = f'{self.sender}{self.receiver}{self.amount}{self.timestamp}'.encode()
        self.signature = sk.sign(message).hex()

    def verify_transaction(self):
        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(self.sender), curve=ecdsa.SECP256k1)
        message = f'{self.sender}{self.receiver}{self.amount}{self.timestamp}'.encode()
        return vk.verify(bytes.fromhex(self.signature), message)