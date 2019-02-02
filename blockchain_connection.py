from blockchain import Transaction, Block

import socket
import requests
import json

from blockchain_http import genesis_port


def dump_block(block):
    return {"b_hash": block.hash, "p_hash": block.prev_hash}


def parse_request(request):
    return json.loads(json.dumps(request.json()))


def sync_admin_server(adm_ip, adm_port, block_chain, name):
    request_data = [dump_block(block) for block in block_chain.chain]
    request_data.append({"reward": block_chain.mining_reward})
    request_data.append({"name": name})

    response = requests.post("http://"+adm_ip+':'+str(adm_port)+"/api/v2/sync/",
                             json=json.dumps(request_data))
    return response


def transactions_deserializer(transactions_json):
    transactions = []
    for trx in transactions_json:
        trs = Transaction(trx['f_address'], trx['t_address'], trx['amount'])
        trs.timestamp = trx['timestamp']
        trs.signature = trx['signature']
        transactions.append(trs)

    return transactions


def chain_deserializer(chain_json):
    chain = []
    for block_json in chain_json:
        transactions = transactions_deserializer(block_json['transactions'])
        block_to_append = Block(block_json['timestamp'],
                            transactions,
                            block_json['prev_hash'])
        block_to_append.nonce = block_json['nonce']
        block_to_append.hash = block_json['hash']

        chain.append(block_to_append)

    return chain


def json_initializer(request) -> tuple:
    output = request.form
    try:
        init_tuple = (output["name"], output["IP"])
    except KeyError as error:
        print("Cannot find " + str(error))
        return None

    return init_tuple


def connect_genesis_server(genesis_ip: str):
    peer_data = {"name": socket.gethostname(), "IP": 'localhost'}
    requests.post("http://"+genesis_ip+":"+genesis_port+"/connect", data=peer_data)


def return_peers(genesis_ip: str) -> list:
    return list(json.loads(json.dumps(requests.get("http://+" + genesis_ip + ":5000/connect").json())))
