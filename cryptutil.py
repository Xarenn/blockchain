from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256

def sign_hash(hash, priv_key):
    signer = PKCS1_v1_5.new(priv_key)
    digest = SHA256.new()
    digest.update(hash)
    return signer.sign(digest)

def verify_hash(hash, sign, pub_key):
    signer = PKCS1_v1_5.new(pub_key)
    digest = SHA256.new()
    digest.update(hash)
    return signer.verify(digest, sign)