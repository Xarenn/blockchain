from Crypto.PublicKey import RSA
from base64 import b64encode, b64decode
from datetime import datetime

import cryptutil

import hashlib
import json


class BlockChain:

    def __init__(self):
        self.chain = [self.genesis_block()]
        self.pending_transactions = []
        self.level_mining = 3
        self.mining_reward = 20

    def __str__(self) -> str:
        return json.dumps(self,
                          default=lambda o: o.decode('ascii') if type(o) is bytes else o.__dict__,
                          sort_keys=True, indent=4)

    @staticmethod
    def genesis_block():
        return Block(datetime.now(), [], '')

    def mine_block(self, miner_address):
        reward_transaction = Transaction(None, miner_address, self.mining_reward)
        self.pending_transactions.append(reward_transaction)

        block = Block(datetime.now(),
                      self.pending_transactions, self.get_newest_block().hash)
        block.mine(self.level_mining)

        self.chain.append(block)
        self.pending_transactions = []

    def find_transaction_by_hash(self, block_hash):
        for block in self.chain:
            for trx in block.transactions:
                if trx.calculate_hash() == block_hash:
                    return trx

        return None

    def connect(self, chain):
        self.chain = chain

    def get_balance_from_wallet(self, wallet_address) -> int:
        balance = 0
        for block in self.chain:
            for trx in block.transactions:
                if trx.f_address == wallet_address:
                    balance -= trx.amount
                if trx.t_address == wallet_address:
                    balance += trx.amount

        return balance

    def get_newest_block(self):
        return self.chain[len(self.chain)-1]

    def chain_validator(self) -> bool:
        gen_block = self.genesis_block()

        if gen_block != self.chain[0]:
            return False

        for i in range(1, len(self.chain)-1):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.prev_hash != previous_block.calculate_hash():
                return False

        return True

    def add_transaction(self, transaction):
        cash_storage = self.get_balance_from_wallet(transaction.f_address)

        if cash_storage == 0 or transaction.amount > cash_storage:
            raise Exception("Not enough money for transaction")

        if len(transaction.t_address) == 0 and len(transaction.f_address) == 0:
            raise Exception("Transaction should have from and to address")

        if transaction.verify() is False:
            raise Exception("Cannot add transaction to chain")

        self.pending_transactions.append(transaction)


class Transaction:

    def __init__(self, from_address, t_address, amount):
        self.f_address = from_address
        self.t_address = t_address
        self.amount = amount
        self.timestamp = str(datetime.now())
        self.signature = ""

    def __str__(self) -> str:
        return json.dumps(self, default=lambda o: o.decode('ascii') if type(o) is bytes else o.__dict__
                          , sort_keys=True, indent=4)

    def __eq__(self, other) -> bool:
        try:
            ne = (self.timestamp == other.timestamp
                    and self.f_address == other.f_address
                    and self.t_address == other.t_address
                    and self.amount == other.amount)

        except AttributeError:
            ne = (other is None and len(str(self.timestamp)) > 0 and len(str(self.f_address)) > 0
                and len(str(self.t_address)) > 0 and self.amount is not None)

        return ne

    def __ne__(self, other) -> bool:
        try:
            ne = (self.timestamp != other.timestamp
                    and self.f_address != other.f_address
                    and self.t_address != other.t_address
                    and self.amount != other.amount)

        except AttributeError:
            ne = (other is None and len(str(self.timestamp)) > 0 and len(str(self.f_address)) > 0
                and len(str(self.t_address)) > 0 and self.amount is not None)

        return ne

    def sign(self, sign_key):

        if sign_key.publickey().exportKey("PEM") != self.f_address.encode():
            raise Exception("Cannot sign other wallets")

        calculated_hash = self.calculate_hash()
        sign = cryptutil.sign_hash(calculated_hash.encode(), sign_key)
        self.signature = b64encode(sign)

    def verify(self) -> bool:

        if len(self.f_address) == 0:
            return True

        if self.signature is None or len(self.signature) == 0:
            raise Exception("No signature in transaction")

        key = RSA.importKey(self.f_address)
        return cryptutil.verify_hash(self.calculate_hash().encode(), b64decode(self.signature), key)

    def calculate_hash(self):
        return (hashlib.sha256(self.encode_v(self.f_address) +
                               self.encode_v(self.t_address) +
                               self.encode_v(self.amount) +
                               self.encode_v(self.timestamp)).hexdigest())

    @staticmethod
    def encode_v(value):
        return str(value).encode('utf-8')


class Block:

    def __init__(self, timestamp, transactions, previous_hash = ""):
        self.timestamp = str(timestamp)
        self.transactions = transactions
        self.prev_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def __str__(self) -> str:
        return json.dumps(self,
          default=lambda o: o.decode('ascii') if type(o) is bytes else o.__dict__,
          sort_keys=True, indent=4)

    def __eq__(self, other) -> bool:
        return (self.timestamp == other.timestamp
                    and self.transactions != other.transactions
                    and self.hash == other.prev_has)

    def __ne__(self, other) -> bool:
        return (self.timestamp != other.timestamp
                    and self.transactions != other.transactions
                    and self.hash != other.prev_has)

    @staticmethod
    def encode_v(value):
        return str(value).encode('utf-8')

    def add_transaction(self, trx):
        self.transactions.append(trx)

    def calculate_hash(self):
        return hashlib.sha256(self.encode_v(self.timestamp)
                            + self.encode_v(self.transactions)
                            + self.encode_v(self.prev_hash)
                            + self.encode_v(self.nonce)).hexdigest()

    def mine(self, mine_level):
        try:
            while self.hash[:mine_level] != "0"*mine_level:
                self.nonce += 1
                self.hash = self.calculate_hash()
        except KeyboardInterrupt:
            print("Nonce value: " + str(self.nonce) + '\n' + "Hash: " + self.hash)
