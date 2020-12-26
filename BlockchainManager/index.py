import glob
import os

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15

from datetime import datetime
import hashlib
import json

######################################################
### Classes for essentials of blockchain structure ###
######################################################

class Transaction:
    def __init__(self, sender, receiver, amount,fee):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.fee=fee
        self.txid = SHA256.new(self.get_json().encode('UTF-8'))
        signer = pkcs1_15.new(sender)
        self.signature = signer.sign(self.txid)

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
        self.nodeNumber=nodeNumber
        self.currentKeys=[]
        self.takeKeysfromFolder()
        #if there is no key in folder structure create first one
        if (len(self.currentKeys)==0):
            self.createNewKey()
            self.UserId=self.getLastKeyfromList()
            ####SİLİNECEK COMMENT####
            #ödev dosyasında böyle bir şey geçiyodu..kaldırabiliriz#
            #id olarak public key kullanılması mevzusu..
        self.nodeId=0
        self.minimumFee = 0.5
        self.pendingBalance=0
        self.spendableBalance=0
    def getBalance(self):
        return self.balance

    def takeKeysfromFolder(self):
        os.chdir('NodeInfoFolder/'+str(self.nodeNumber))

        for filename in glob.glob('*.pem'):
            with open(os.path.join(os.getcwd(), filename), 'r') as f:  # open in readonly mode
                key = RSA.import_key(f.read())
                keyPair = {"private": key.export_key('PEM'), "public": key.publickey().exportKey(format("PEM"))}
                self.currentKeys.append(keyPair)
        os.chdir("..")
        os.chdir("..")


    def setKeys(self, publicKey):
        #çözemedim :)
        pass

    def createNewKey(self):
        key = RSA.generate(2048)
        f = open('NodeInfoFolder/'+str(self.nodeNumber)+'/mykey_'+str(len(self.currentKeys))+'.pem', 'wb+')
        f.write(key.publickey().export_key('PEM'))
        f.close()

        keyPair={"private": key.export_key('PEM'), "public": key.publickey().exportKey(format("PEM"))}
        self.currentKeys.append(keyPair)
        pass

    def getLastKeyfromList(self):
        return self.currentKeys[-1]["public"]
    def getKeyfromList(self,index):
        return self.currentKeys[index]["public"]

    def makeTransaction(self, fee, amount, destination):
        if(fee<self.minimumFee):
            print("You have to give minimum 0.5 as fee !")
            return False

        if (self.spendableBalance < (amount+fee)):
            print("you havent sufficient amount in your balance")
            return False
        t = Transaction(self.getLastKeyfromList, destination, amount,fee)

        verifier = pkcs1_15.new(self.getLastKeyfromList)
        v_hash = SHA256.new()
        v_hash.update(t.get_json().encode('UTF-8'))
        '''
        Network should verify transaction
        try:
            verifier.verify(v_hash, t.signature)
            user = get_user_from_id(receiver_pub_id)
            user.balance = user.balance + amount
            self.balance = self.balance - amount
            return t
        except ValueError:
            print("Transaction is not valid !")
            return 0
        '''
        pass

    def onNewTransactionCame(self,amount):
        self.pendingBalance=self.pendingBalance+amount
    def onTransactionBecomeValid(self,amount):
        self.pendingBalance=self.pendingBalance-amount
        self.spendableBalance=self.spendableBalance+amount

    def getBestBlock(self):
        pass
