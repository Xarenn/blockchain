from random import randint
from flask import Flask, render_template, request
from blockchain import BlockChain, Transaction
from blockchain_connection import json_initializer, parse_request, chain_deserializer, return_peers

import argparse
import json
import requests
import socket
import cryptutil

app = Flask(__name__)
block_chain = BlockChain()
peers = []
genesis_port = 5000


@app.route("/mine", methods=['POST', 'GET'])
def mine_block_endpoint():
    try:
        wallet_address = request.form.get('wallet_address')
        if request.method == 'POST':
            if wallet_address is not None:

                block_chain.mine_block(wallet_address)
                return render_template('mine.html', authorization=True, progress=100)
            else:
                return render_template('mine.html', authorization=False, progress=0)

        if wallet_address is None:
            return render_template('mine.html', authorization=None, progress=0)

    except KeyError as error:
        print("Cannot find " + str(error))
        return render_template('mine.html', authorization=None, progress=0)

    return render_template('mine.html', authorization=None, progress=0)


@app.route('/state')
def block_chain_state():
    return str(block_chain)


@app.route('/transactions_state')
def transactions_state():
    transactions = [str(trx) for block in block_chain.chain for trx in block.transactions]
    return str(transactions)


@app.route('/transactions', methods=['POST', 'GET'])
def block_chain_transactions():
    if request.args.get("hash") is None:
        return render_template('transactions.html', block_chain=block_chain.chain)

    trx = block_chain.find_transaction_by_hash(request.args.get("hash"))
    if trx is not None:
        return render_template('transaction.html', transaction=trx)

    return render_template('transactions.html', block_chain=block_chain.chain)


@app.route("/")
def block_chain_entry():
    return render_template('base.html', block_chain=block_chain.chain, peers=peers)


@app.route("/connect", methods=['POST', 'GET'])
def initialization_p2p():
    if request.method == 'POST':
        init_tuple = json_initializer(request)
        if init_tuple is not None:
            peers.append(init_tuple)
            return json.dumps("SUCCESS CONNECTION")
        else:
            return json.dumps("JSON INVALID")

    if request.method == 'GET':
        return json.dumps(peers)

def synchronize_chain(sync_block_chain: list):
    global block_chain
    block_chain = sync_block_chain

def prepare():
    pub, prv = cryptutil.fake_new_keys(2048)
    pub2, prv2 = cryptutil.fake_new_keys(2048)

    pub_txt = pub.exportKey("PEM").decode('ascii')
    pub2_txt = pub2.exportKey("PEM").decode('ascii')

    block_chain.mine_block(pub_txt)
    block_chain.mine_block(pub2_txt)
    block_chain.mine_block(pub_txt)

    trx = Transaction(pub_txt, pub2_txt, 10)
    trx.sign(prv)
    block_chain.add_transaction(trx)

    trx = Transaction(pub_txt, pub2_txt, 10)
    trx.sign(prv)
    block_chain.add_transaction(trx)

    block_chain.mine_block(pub_txt)


if __name__ == "__main__":
    prepare()
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', type=str)
    parser.add_argument('-port', type=int)

    #ip = requests.get('https://api.ipify.org').text EXTERNAL IP SERVICE

    peers.append(('127.0.0.1', socket.gethostname()))
    args = vars(parser.parse_args())
    if args['ip'] is not None and args['port'] is not None:
        block_chain_req = parse_request(requests.get("http://localhost:5000/state"))
        chain = chain_deserializer(block_chain['chain'])
        synchronize_chain(chain)
        peers = return_peers('127.0.0.1')
        print(peers)
        app.run('127.0.0.1', genesis_port+randint(0,10))
    else:
        app.run('127.0.0.1', genesis_port)