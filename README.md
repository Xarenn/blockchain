# BlockChain
Blockchain implementation based on (structure functonalities) https://bitcoin.org/bitcoin.pdf

P2P created with FLASK Python3

## How to run it?

Use docker command: <code>docker build . -t block_chain</code>

You can use too this command:
<code>python3 -m pip install -r requirements.txt after installation use python3 blockchain_http.py</code>

## How does it works?

So we create the chain with genesis block it's a base block for the chain. The mining theory was described widely in https://en.bitcoin.it/wiki/Mining

I used the SHA256 hash algorithm to create the block's hash, mine_difficulty was solved by adding n zeros prefix to the proposed hash and by incrementing nonce value.

PyCrypto with RSA 2048 size keys used to sign transactions (signing use private_key).

We can mining, adding transactions to the wallet, create wallet (public key is the address of the wallet)

Basic functionalities and structure was implemented, it's a POC.


![Alt text](img/blocks.png?raw=true "Blocks")
![Alt text](img/transactions.png?raw=true "Transactions")


