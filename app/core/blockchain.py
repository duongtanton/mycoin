import json
import time
from app.core.transaction import Transaction
from app.core.wallet import Wallet


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.wallets = {}

    def create_genesis_block(self):
        self.new_block(previous_hash='0')

    def new_block(self, previous_hash):
        block = {
            'index': len(self.chain),
            'timestamp': int(time.time()),
            'transactions': self.current_transactions,
            'previous_hash': previous_hash
        }
        self.chain.append(block)
        self.current_transactions = []
        return block

    def add_wallet(self, wallet):
        self.wallets[wallet.address] = wallet

    def get_wallet_by_address(self, address):
        return self.wallets.get(address)

    def new_transaction(self, sender_address, receiver_address, amount, sender_private_key):
        sender_wallet = self.get_wallet_by_address(sender_address)
        receiver_wallet = self.get_wallet_by_address(receiver_address)

        if sender_wallet is None or receiver_wallet is None:
            return False
        
        transaction = Transaction(sender_address, receiver_address, amount)
        transaction.sign_transaction(sender_private_key)

        if transaction.verify_transaction():
            self.current_transactions.append(transaction)
            sender_wallet.balance -= amount
            receiver_wallet.balance += amount
            sender_wallet.add_transaction_to_history(transaction)
            receiver_wallet.add_transaction_to_history(transaction)
            return True
        return False

    def get_wallet_statistics(self, address):
        wallet = self.get_wallet_by_address(address)
        if wallet:
            return {
                'address': wallet.address,
                'balance': wallet.balance,
                'transaction_history': [vars(tx) for tx in wallet.transaction_history]
            }
        else:
            return None

# Example usage
blockchain = Blockchain()

# Create wallets
wallet1 = Wallet()
wallet2 = Wallet()

blockchain.add_wallet(wallet1)
blockchain.add_wallet(wallet2)

# Perform transactions
wallet1.balance = 100
blockchain.new_transaction(wallet1.address, wallet2.address, 30, wallet1.private_key)

# View wallet statistics
wallet1_stats = blockchain.get_wallet_statistics(wallet1.address)
if wallet1_stats:
    print(f"Wallet 1 Statistics:\n{json.dumps(wallet1_stats, indent=4)}")
else:
    print("Wallet not found.")
