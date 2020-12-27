import glob
import os

from Crypto.PublicKey import RSA, ECC
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15, DSS

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

class GenesisBlock:
    def __init__(self, genesisTransaction):
        self.content = {"transactions": [], "awardTx": genesisTransaction.getTransaction()}
        self.id = SHA256.new(str.encode(json.dumps(self.content)))

    def getBlock(self):
        block = {"id": self.id.hexdigest(), "content": self.content}
        return json.dumps(block)

class GenesisTransaction:
    def __init__(self, privKey):
        self.inputs = []
        self.outputs = [{"receiver" : ECC.import_key(privKey).public_key().export_key(format="PEM"), "amount": 100}]
        self.id = SHA256.new(str.encode(self.getJson()))
        self.signature = DSS.new(ECC.import_key(privKey), 'fips-186-3').sign(self.id)

    def getJson(self):
        content = {"inputs": self.inputs, "outputs": self.outputs}
        return json.dumps(content)

    def getTransaction(self):
        transaction = {"id": self.id.hexdigest(), "signature": self.signature.hex(), "content": self.getJson()}
        return json.dumps(transaction)

class BlockchainManager:
    def __init__(self, server):
        self.server = server
        self.allKeys = list()
        self.allTransactions = {}
        self.allBlocks = []
        self.currentKey = {}  # {name, private, public}

        self.setPreviousKeys()
        self.setPreviousTransactions()
        self.setPreviousBlocks()

        self.currentKeys = []
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

    def setPreviousKeys(self):
        with open("./NodeInfoFolder/" + str(self.server.myNodeId) + "/keys.json") as f:
            allKeysJson = json.load(f)
            self.allKeys = allKeysJson["keys"]
            f.close()

        #  if this is the first node and no previous key in the system
        if len(self.allKeys) == 0 and self.server.myNodeId == 1:
            self.startGenesisOfBlockchain()

        else:
            self.currentKey = self.allKeys[-1]

    def setPreviousTransactions(self):
        with open("./NodeInfoFolder/" + str(self.server.myNodeId) + "/transactions.json") as f:
            self.allTransactions = json.load(f)
            f.close()

    def setPreviousBlocks(self):
        with open("./NodeInfoFolder/" + str(self.server.myNodeId) + "/blocks.json") as f:
            self.allBlocks = json.load(f)["blocks"]
            f.close()


    def startGenesisOfBlockchain(self):
        self.addNewKey("mbKey")
        self.selectKey("mbKey")
        genesisTransaction = GenesisTransaction(self.currentKey["private"])
        self.saveTransaction(genesisTransaction)
        genesisBlock = GenesisBlock(genesisTransaction)


        with open("./NodeInfoFolder/" + str(self.server.myNodeId) + "/blocks.json", "w") as f:
            json.dump({"blocks": [genesisBlock.getBlock()]}, f)
            f.close()

    def saveTransaction(self, transactionObject):
        self.allTransactions.update({transactionObject.id.hexdigest(): transactionObject.getTransaction()})
        with open("./NodeInfoFolder/" + str(self.server.myNodeId) + "/transactions.json", "w") as f:
            json.dump(self.allTransactions, f)
            f.close()



    def selectKey(self, keyName):
        for key in self.allKeys:
            if key["name"] == keyName:
                self.currentKey = key
                break
        #  secilmis olan hesap icin balance bulma vs methodlarini burada cagiracagiz.


    def addNewKey(self, name):
        key = ECC.generate(curve='P-256')
        newKeyObject = {"name": name,
                        "private": key.export_key(format="PEM"),
                        "public": key.public_key().export_key(format="PEM")}

        self.allKeys.append(newKeyObject)
        with open("./NodeInfoFolder/" + str(self.server.myNodeId) + "/keys.json", "w") as f:
            json.dump({"keys": self.allKeys}, f)
            f.close()

#########################################################################################################
    ######################################################################################################
    ######################################################################################################

    def getBalance(self):
        return self.balance

    def takeKeysfromFolder(self):
        os.chdir('NodeInfoFolder/'+str(self.server.myNodeId))

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
        f = open('NodeInfoFolder/'+str(self.server.myNodeId)+'/mykey_'+str(len(self.currentKeys))+'.pem', 'wb+')
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
