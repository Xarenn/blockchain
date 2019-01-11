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


class Transaction:
    def __init__(self, fAddress, tAddress, amount):
        self.f_address = fAddress
        self.t_address = tAddress
        self.amount = amount
        self.timestamp="2/11/2019" #date.now()

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__,
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



class Block:
    def __init__(self, timestamp, transactions, prevHash = ""):
        self.timestamp = timestamp
        self.transactions = transactions
        self.prev_hash = prevHash
        self.hash = self.calculate_hash()

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__,
           sort_keys=True, indent=2)

    def __eq__(self, other):
        return (self.timestamp == other.timestamp
                    and self.transtactions == other.transactions
                    and self.hash == other.prev_has)

    def __ne__(self, other):
        return (self.timestamp != other.timestamp
                    and self.transtactions != other.transactions
                    and self.hash != other.prev_has)

    def encode_v(self, value):
        return str(value).encode('utf-8')

    def add_transaction(self, trx):
        self.transactions.append(trx)

    def get_hash():
        return self.hash

    def calculate_hash(self):
        return hashlib.sha256(self.encode_v(self.timestamp)
                     +self.encode_v(self.transactions)
                     + self.encode_v(self.prev_hash)).hexdigest()


b = BlockChain()
b.mine_block()
b.mine_block()
print (str(b))
print(b.chain_validator())
print("-"*10+"fail chain"+"-"*10)
b.chain[1].hash = "1234123"
print(str(b))
print(b.chain_validator())

