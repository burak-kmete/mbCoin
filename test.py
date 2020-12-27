from Crypto.PublicKey import RSA, ECC
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from Crypto.Signature import DSS


global tx_id
from datetime import datetime
import hashlib
import json


# key yaratma
key = ECC.generate(curve='P-256')

# priv key export
privkey = key.export_key(format="PEM")
#print(privkey)
# pub key export
pubkey = key.public_key().export_key(format="PEM")
#print(pubkey)

mystring = "deneme string verim"

# sha256 hashing
h = SHA256.new(str.encode(mystring))

# signing a hash with priv key
signer = DSS.new(ECC.import_key(privkey), 'fips-186-3')
signiture = signer.sign(h)
print(signiture.hex())

# singiture verification with pubkey and signiture
h2 = SHA256.new(str.encode(mystring))
verifier = DSS.new(ECC.import_key(pubkey), 'fips-186-3')
verifier.verify(h2, signiture)

priki = """-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgC68cODTBDF8hadeJ
lVQFWzxWXmgjzCbozorY2SeNBgGhRANCAAQ2//gxsV4dBZhlkNafrI+DRHU+bUx2
mxI7ZYC11jf+Lw9vUH87B42uD53Ozi18NvGcQtSrFzQtwhp9+r1G2U1q
-----END PRIVATE KEY-----"""

print(ECC.import_key(priki).public_key().export_key(format="PEM") == """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAENv/4MbFeHQWYZZDWn6yPg0R1Pm1M
dpsSO2WAtdY3/i8Pb1B/OweNrg+dzs4tfDbxnELUqxc0LcIaffq9RtlNag==
-----END PUBLIC KEY-----""")

"""-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAENv/4MbFeHQWYZZDWn6yPg0R1Pm1M
dpsSO2WAtdY3/i8Pb1B/OweNrg+dzs4tfDbxnELUqxc0LcIaffq9RtlNag==
-----END PUBLIC KEY-----"""
