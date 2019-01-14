import binascii
from base64 import b64encode, b64decode
from datetime import datetime

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

import cryptutil

import hashlib
import json

class BlockChain:
    def __init__(self):
        self.chain = [self.genesis_block()]
        self.pending_transactions = []
        self.level_mining = 2
        self.mining_reward = 1

    def __str__(self):
        return json.dumps(self, default=
        lambda o: o.decode('ascii') if type(o) is bytes else o.__dict__,
           sort_keys=True, indent=4)

    def genesis_block(self):
        return Block(datetime.now(), [], 0, '')

    def mine_block(self, minerAddress):
        self.mining_reward *= len(self.chain)
        reward_transaction = Transaction(None, minerAddress, self.mining_reward)
        self.pending_transactions.append(reward_transaction)

        block = Block(datetime.now(),
                      self.pending_transactions, self.mining_reward, self.get_newest_block().hash)
        block.mine(self.level_mining)

        self.chain.append(block)
        self.pending_transactions = []

    def get_newest_block(self):
        return self.chain[len(self.chain)-1]

    def chain_validator(self):
        gen_block = self.genesis_block()

        if(gen_block != self.chain[0]):
            return False

        for i in range(1, len(self.chain)-1):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if((current_block.hash != current_block.calculate_hash())):
                return False

            if((current_block.prev_hash != previous_block.calculate_hash())):
                return False

        return True

    def add_transaction(self, transaction):
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

    def __str__(self):
        return json.dumps(self, default=
        lambda o: o.decode('ascii') if type(o) is bytes else o.__dict__,
           sort_keys=True, indent=4)

    def __eq__(self, other):
        return (self.timestamp == other.timestamp
                    and self.fAddress == other.fAddress
                    and self.tAddress == other.tAddress
                    and self.amount == other.amount)

    def __ne__(self, other):
        return (self.timestamp != other.timestamp
                    and self.fAddress != other.fAddress
                    and self.tAddress != other.tAddress
                    and self.amount != other.amount)

    def sign(self, sign_key):

        if(sign_key.publickey().exportKey("PEM") != self.f_address.encode()):
            raise Exception("Cannot sign other wallets")

        hash = self.calculate_hash()
        sign = cryptutil.sign_hash(hash.encode(), sign_key)
        self.signature = b64encode(sign)

    def verify(self):

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
    def __init__(self, timestamp, transactions, balance, prevHash = ""):
        self.timestamp = str(timestamp)
        self.transactions = transactions
        self.prev_hash = prevHash
        self.nonce = 0
        self.balance = balance
        self.hash = self.calculate_hash()

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__,
           sort_keys=True, indent=2)

    def __eq__(self, other):
        return (self.timestamp == other.timestamp
                    and self.transactions != other.transactions
                    and self.hash == other.prev_has)

    def __ne__(self, other):
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
        while(self.hash[:mineLevel] != "0"*mineLevel):
            self.nonce += 1
            self.hash = self.calculate_hash()


b = BlockChain()
pub, prv = cryptutil.fake_new_keys(2048)
pub2, prv2 = cryptutil.fake_new_keys(2048)

b.mine_block(pub.exportKey("PEM").decode('ascii'))
b.mine_block(pub2.exportKey("PEM").decode('ascii'))
b.mine_block(pub.exportKey("PEM").decode('ascii'))

trx = Transaction(pub.exportKey("PEM").decode('ascii'), pub2.exportKey("PEM").decode('ascii'), 10)
trx.sign(prv)
b.add_transaction(trx)

trx = Transaction(pub.exportKey("PEM").decode('ascii'), pub2.exportKey("PEM").decode('ascii'), 10)
trx.sign(prv)

b.add_transaction(trx)

b.mine_block(pub.exportKey("PEM").decode('ascii'))

print (str(b))
print(b.chain_validator())

#print("-"*10+"fail chain"+"-"*10)
#b.chain[1].hash = "1234123"
#print(str(b))
#print(b.chain_validator())

