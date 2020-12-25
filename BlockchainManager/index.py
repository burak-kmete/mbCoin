import glob
import os

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15

global tx_id
from datetime import datetime
import hashlib
import json

######################################################
### Classes for essentials of blockchain structure ###
######################################################

tx_id = 0

class Transaction:
    def __init__(self, sender, receiver, amount):
        global tx_id
        self.txid = tx_id
        tx_id = tx_id + 1
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        h = SHA256.new(self.get_json().encode('UTF-8'))
        signer = pkcs1_15.new(sender)
        self.signature = signer.sign(h)

    def get_json(self):
        x = {
            "id": self.txid,
            "sender": self.sender.publickey().exportKey(format("OpenSSH")).decode(),
            "receiver": self.receiver,
            "amount": self.amount
        }
        return json.dumps(x)

class BlockchainManager:
    def __init__(self,nodeNumber):
        self.currentKeys = []
        self.nodeId=0
        self.nodeNumber=nodeNumber
        self.minimumFee = 0.5
        self.createNewKey()
    def getBalance(self):
        pass

    def takeKeysfromFolder(self):
        os.chdir('NodeInfoFolder/'+str(self.nodeNumber))

        for filename in glob.glob('*.pem'):
            with open(os.path.join(os.getcwd(), filename), 'r') as f:  # open in readonly mode
                key = RSA.import_key(f.read())
                keyPair = {"private": key.export_key('PEM'), "public": key.publickey().exportKey(format("PEM"))}
                self.currentKeys.append(keyPair)

    def setKeys(self, publicKey):
        pass

    def createNewKey(self):
        key = RSA.generate(2048)

        f = open('NodeInfoFolder/'+str(self.nodeNumber)+'/mykey_'+str(len(self.currentKeys))+'.pem', 'wb')
        f.write(key.export_key('PEM'))
        f.close()

        keyPair={"private": key.export_key('PEM'), "public": key.publickey().exportKey(format("PEM"))}
        self.currentKeys.append(keyPair)
        pass

    def makeTransaction(self, fee, amount, destination):
        pass

    def getBestBlock(self):
        pass
