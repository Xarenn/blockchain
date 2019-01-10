import hashlib
import json

class BlockChain:
    def __init__(self):
        self.chain = [self.genesis_block()]
        self.pending_transactions = []

    def genesis_block(self):
        return Block("12/12/2009", [], '')

    def mine_block(self):
        self.chain.append(Block("13/11/2010", [], self.get_newest_block().hash))

    def get_newest_block(self):
        return self.chain[len(self.chain)-1]

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__,
           sort_keys=True, indent=4)

    def chain_validator():
        gen_block = self.genesis_block()
        if(gen_block != genesis_block()):


class Transaction:
    def __init__(self, fAddress, tAddress, amount):
        self.f_address = fAddress
        self.t_address = tAddress
        self.amount = amount

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__,
           sort_keys=True, indent=4)

class Block:
    def __init__(self, timestamp, transactions, prevHash = ""):
        self.timestamp = timestamp
        self.transactions = transactions
        self.prev_hash = prevHash
        self.hash = self.calculate_hash()

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__,
           sort_keys=True, indent=2)

    def encode_v(self, value):
        return str(value).encode('utf-8')

    def add_transaction(self, trx):
        self.transactions.append(trx)

    def get_hash():
        return self.hash

    def calculate_hash(self):
        return hashlib.sha256(self.encode_v(self.timestamp)+
                     self.encode_v(self.transactions)
                     + self.encode_v(self.prev_hash)).hexdigest()


b = BlockChain()
b.mine_block()
b.mine_block()
print (str(b))
