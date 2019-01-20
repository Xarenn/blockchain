from base64 import b64encode

from flask import Flask, render_template, request
from blockchain import BlockChain, Transaction

import cryptutil

app = Flask(__name__)
block_chain = BlockChain()

@app.route("/mine", methods=['POST', 'GET'])
def mine_block_endpoint():
    try:
        if(request.get_json().get('hash') == None):
            return render_template('base.html', authorize="NotAuthorized")

    except KeyError as error:
        print("Cannot find " + str(error))
        return render_template('base.html', authorize="NotAuthorized")

    return render_template('base.html', authorize = request.get_json()['hash'])

@app.route('/state')
def block_chain_state():
    return str(block_chain)

@app.route('/transactions', methods=['POST', 'GET'])
def block_chain_transactions():
    if(request.args.get("hash") == None):
        return render_template('transactions.html', block_chain=block_chain.chain)

    trx = block_chain.find_transaction_by_hash(request.args.get("hash"))
    if(trx != None):
        return render_template('transaction.html', transaction = trx)

    return render_template('transactions.html', block_chain = block_chain.chain)

@app.route("/")
def block_chain_entry():
    return render_template('base.html', block_chain = block_chain.chain)

def prepare():
    pub, prv = cryptutil.fake_new_keys(2048)
    pub2, prv2 = cryptutil.fake_new_keys(2048)

    block_chain.mine_block(pub.exportKey("PEM").decode('ascii'))
    block_chain.mine_block(pub2.exportKey("PEM").decode('ascii'))
    block_chain.mine_block(pub.exportKey("PEM").decode('ascii'))

    trx = Transaction(pub.exportKey("PEM").decode('ascii'), pub2.exportKey("PEM").decode('ascii'), 10)
    trx.sign(prv)
    block_chain.add_transaction(trx)

    trx = Transaction(pub.exportKey("PEM").decode('ascii'), pub2.exportKey("PEM").decode('ascii'), 10)
    trx.sign(prv)
    block_chain.add_transaction(trx)

    block_chain.mine_block(pub.exportKey("PEM").decode('ascii'))

if( __name__ == "__main__"):
    prepare()
    app.run()