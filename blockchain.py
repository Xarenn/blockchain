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

    def genesis_block(self):
        return Block(datetime.now(), [], '')

    def mine_block(self, minerAddress):
        reward_transaction = Transaction(None, minerAddress, self.mining_reward)
        self.pending_transactions.append(reward_transaction)

        block = Block(datetime.now(),
                      self.pending_transactions, self.get_newest_block().hash)
        block.mine(self.level_mining)

        self.chain.append(block)
        self.pending_transactions = []

    def find_transaction_by_hash(self, hash):
        for block in self.chain:
            for trx in block.transactions:
                if (trx.calculate_hash() == hash):
                    return trx

        return None

    def connect(self, chain):
        self.chain = chain

    def get_balance_from_wallet(self, walletAddress) -> int:
        balance = 0
        for block in self.chain:
            for trx in block.transactions:
                if(trx.f_address == walletAddress):
                   balance -= trx.amount
                if(trx.t_address == walletAddress):
                    balance += trx.amount

        return balance

    def get_newest_block(self):
        return self.chain[len(self.chain)-1]

    def chain_validator(self) -> bool:
        gen_block = self.genesis_block()

        if(gen_block != self.chain[0]):
            return False

        for i in range(1, len(self.chain)-1):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if(current_block.hash != current_block.calculate_hash()):
                return False

            if(current_block.prev_hash != previous_block.calculate_hash()):
                return False

        return True

    def add_transaction(self, transaction):
        cash_storage = self.get_balance_from_wallet(transaction.f_address)

        if(cash_storage == 0 or transaction.amount > cash_storage):
            raise Exception("Not enough money for transaction")

        if(len(transaction.t_address) == 0 and len(transaction.f_address) == 0):
            raise Exception("Transaction should have from and to address")

        if(transaction.verify() == False):
            raise Exception("Cannot add transaction to chain")

        self.pending_transactions.append(transaction)


class Transaction:

    def __init__(self, fAddress, tAddress, amount):
        self.f_address = fAddress
        self.t_address = tAddress
        self.amount = amount
        self.timestamp = str(datetime.now())
        self.signature = ""

    def __str__(self) -> str:
        return json.dumps(self,
          default=lambda o: o.decode('ascii') if type(o) is bytes else o.__dict__,
          sort_keys=True, indent=4)

    def __eq__(self, other) -> bool:
        return (self.timestamp == other.timestamp
                    and self.f_address == other.f_address
                    and self.t_address == other.t_address
                    and self.amount == other.amount)

    def __ne__(self, other) -> bool:
        try:
            ne = (self.timestamp != other.timestamp
                    and self.f_address == other.f_address
                    and self.t_address == other.t_address
                    and self.amount != other.amount)
        except AttributeError:
            ne = (other == None and len(str(self.timestamp)) > 0 and len(str(self.f_address)) > 0
                and len(str(self.t_address)) > 0 and self.amount != None)

        return ne

    def sign(self, sign_key):

        if(sign_key.publickey().exportKey("PEM") != self.f_address.encode()):
            raise Exception("Cannot sign other wallets")

        hash = self.calculate_hash()
        sign = cryptutil.sign_hash(hash.encode(), sign_key)
        self.signature = b64encode(sign)

    def verify(self) -> bool:

        if(len(self.f_address) == 0):
            return True

        if((self.signature == None) and (len(self.signature) == 0)):
            raise Exception("No signature in transaction")

        key = RSA.importKey(self.f_address)
        return cryptutil.verify_hash(self.calculate_hash().encode(), b64decode(self.signature), key)

    def calculate_hash(self):
        return (hashlib.sha256(self.encode_v(self.f_address)+
                               self.encode_v(self.t_address)+
                               self.encode_v(self.amount)+
                               self.encode_v(self.timestamp)).hexdigest())

    def encode_v(self, value):
        return str(value).encode('utf-8')


class Block:

    def __init__(self, timestamp, transactions, prevHash = ""):
        self.timestamp = str(timestamp)
        self.transactions = transactions
        self.prev_hash = prevHash
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

    def encode_v(self, value):
        return str(value).encode('utf-8')

    def add_transaction(self, trx):
        self.transactions.append(trx)

    def calculate_hash(self):
        return hashlib.sha256(self.encode_v(self.timestamp)
                            + self.encode_v(self.transactions)
                            + self.encode_v(self.prev_hash)
                            + self.encode_v(self.nonce)).hexdigest()

    def mine(self, mineLevel):
        try:
            while(self.hash[:mineLevel] != "0"*mineLevel):
                self.nonce += 1
                self.hash = self.calculate_hash()
        except KeyboardInterrupt:
            print("Nonce value: " + str(self.nonce) + '\n' + "Hash: " + self.hash)


#b = BlockChain()
#pub, prv = cryptutil.fake_new_keys(2048)
#pub2, prv2 = cryptutil.fake_new_keys(2048)

#b.mine_block(pub.exportKey("PEM").decode('ascii'))
#b.mine_block(pub2.exportKey("PEM").decode('ascii'))
#b.mine_block(pub.exportKey("PEM").decode('ascii'))

#rx = Transaction(pub.exportKey("PEM").decode('ascii'), pub2.exportKey("PEM").decode('ascii'), 10)
#trx.sign(prv)
#b.add_transaction(trx)

#trx = Transaction(pub.exportKey("PEM").decode('ascii'), pub2.exportKey("PEM").decode('ascii'), 10)
#trx.sign(prv)
#b.add_transaction(trx)

#b.mine_block(pub.exportKey("PEM").decode('ascii'))
#print (str(b))
#print(b.chain_validator())

#print (b.get_balance_from_wallet(pub.exportKey("PEM").decode('ascii')))
#print (b.get_balance_from_wallet(pub2.exportKey("PEM").decode('ascii')))

#try:
#   trx = Transaction(pub.exportKey("PEM").decode('ascii'), pub2.exportKey("PEM").decode('ascii'), 50)
    #trx.sign(prv)
    #b.add_transaction(trx)
#except Exception as exc:
 #   print(str(exc))

#print("-"*10+"fail chain"+"-"*10)
#b.chain[1].hash = "1234123"
#print(str(b))
#print(b.chain_validator())

