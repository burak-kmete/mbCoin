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
    def __init__(self, senderPrivkey, senderPubkey, receiverPubkey, amount, fee, isSpecialTx):
        self.isSpecialTx = isSpecialTx
        self.senderPrivkey = senderPrivkey
        if isSpecialTx:
            self.specialAward = 10
            self.content = {"inputs": [], "outputs": [{"receiver":receiverPubkey, "amount": self.specialAward + fee}]}
        else:
            self.content = {"inputs": [], "outputs": [{"receiver": receiverPubkey, "amount": amount}]}
        self.id = SHA256.new(str.encode(self.getContentJson())).hexdigest()

    def getContentJson(self):
        return json.dumps(self.content)

    def getTransactionJson(self):
        if self.isSpecialTx:
            return json.dumps({"content": self.content, "id": self.id})
        else:
            signer = DSS.new(ECC.import_key(self.senderPrivkey), 'fips-186-3')
            signature = signer.sign(self.id).hex()

            return json.dumps({"content": self.getContentJson(), "id":self.id, "signature": signature})


class Block:
    def __init__(self, minerPubkey, txIdList, previousBlockId, isGenesisBlock):
        self.txIdList = txIdList
        if isGenesisBlock:
            self.transactions = []
            self.specialTx = json.loads(Transaction(None, None, minerPubkey, 100, 0, True).getTransactionJson())
            self.previousBlockId = 0
            self.nonce = 0
            self.id = 0
        else:
            pass
    def getContent(self):
        return {"transactions": self.transactions, "specialTx": self.specialTx,
                           "previousBlockId": self.previousBlockId, "nonce": self.nonce}

    def getBlockJson(self):
        return json.dumps({"id": self.id, "content": self.getContent()})



class BlockchainManager:
    def __init__(self, server):
        self.server = server
        self.allKeys = list()
        self.allTransactions = {}
        self.allBlocks = []
        self.currentKey = {}  # {name, private, public}
        self.pendingTransactions = {}

        self.setPreviousKeys()
        self.setPreviousTransactions()
        self.setPreviousBlocks()
        print(2)

    def setPreviousKeys(self):
        with open("./NodeInfoFolder/" + str(self.server.myNodeId) + "/keys.json") as f:
            allKeysJson = json.load(f)
            self.allKeys = allKeysJson["keys"]
            f.close()

        #  if this is the first node and no previous key in the system
        if len(self.allKeys) == 0 and self.server.myNodeId == 1:
            self.startGenesisOfBlockchain()

        else:
            if len(self.allKeys) != 0:
                self.currentKey = self.allKeys[-1]

    def setPreviousTransactions(self):
        with open("./NodeInfoFolder/" + str(self.server.myNodeId) + "/transactions.json") as f:
            self.allTransactions = json.load(f)
            for key, value in self.allTransactions.items():
                self.allTransactions[key] = self.getDictFromTxJson(value)
            f.close()

    def setPreviousBlocks(self):
        with open("./NodeInfoFolder/" + str(self.server.myNodeId) + "/blocks.json") as f:
            self.allBlocks = json.load(f)["blocks"]
            i = 0
            while i < len(self.allBlocks):
                self.allBlocks[i] = self.getDictFromBlockJson(self.allBlocks[i])
                i += 1
            f.close()


    def startGenesisOfBlockchain(self):
        self.addNewKey("mbKey")
        self.selectKey("mbKey")
        genesisBlock = Block(self.currentKey["public"], [], 0, True)
        self.saveTransaction(json.dumps(genesisBlock.specialTx))

        with open("./NodeInfoFolder/" + str(self.server.myNodeId) + "/blocks.json", "w") as f:
            json.dump({"blocks": [genesisBlock.getBlockJson()]}, f)
            f.close()

    def saveTransaction(self, transactionJson):
        self.allTransactions.update({json.loads(transactionJson)["id"]: transactionJson})
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

    def getDictFromTxJson(self, txJson):
        return json.loads(txJson)

    def getDictFromBlockJson(self, block):
        return json.loads(block)

    def txValidityCheck(self, txDict):
        hash = SHA256.new(str.encode(json.dumps(txDict["content"]))).hexdigest()
        if not(hash == txDict["id"]):
            return {"success": False, "error": "Wrong hash, content broken"}
        else:
            expextedMinimumInputAmount = 0.5
            for output in txDict["content"]["outputs"]:
                expextedMinimumInputAmount += output["amount"]

            totalInputAmount = 0

            # SIGNITURE AND PUBKEY CHECK
            for input in txDict["content"]["inputs"]:
                inputTx = self.allTransactions[input["id"]]
                inputTxContent = inputTx["content"]
                outputsOfinputTx = inputTxContent["outputs"]
                try:
                    h2 = SHA256.new(str.encode(json.dumps(inputTxContent)))
                    verifier = DSS.new(ECC.import_key(outputsOfinputTx[int(input["index"])]), 'fips-186-3')
                    verifier.verify(h2, bytes.fromhex(txDict["signature"]))

                except:
                    return {"success": False, "error": "Not authorized to use the output"}

                totalInputAmount += int(outputsOfinputTx[int(input["index"])]["amount"])

            # AMOUNT CHECK
            if totalInputAmount < expextedMinimumInputAmount:
                return {"success": False, "error": "Insufficient input"}

            # DOUBLE SPEND CHECK FOR ACCEPTED BLOCKS
            for key, value in self.allTransactions.items():
                olderTx = self.allTransactions[key]
                for olderTxInput in olderTx["content"]["inputs"]:
                    for newInput in txDict["content"]["inputs"]:
                        if newInput == olderTxInput:
                            return {"success": False, "error": "Double spend"}

            # DOUBLE SPEND CHECK FOR PENDING TRANSACTIONS
            for key, value in self.pendingTransactions.items():
                olderTx = self.allTransactions[key]
                for olderTxInput in olderTx["content"]["inputs"]:
                    for newInput in txDict["content"]["inputs"]:
                        if newInput == olderTxInput:
                            return {"success": False, "error": "Double spend"}

            return {"success": True, "fee": totalInputAmount - expextedMinimumInputAmount + 0.5}

    def getBalance(self):
        spendableCoin = 0
        pending = 0
        outputTxIdIndex = []
        totalInputAmount = 0

        # INPUT TOTAL
        for key, value in self.allTransactions.items():
            i = 0
            while i < len(self.allTransactions[key]["content"]["outputs"]):
                output =  self.allTransactions[key]["content"]["outputs"][i]
                if output["receiver"] == self.currentKey["public"]:
                    totalInputAmount += int(output["amount"])
                    outputTxIdIndex.append({"id": key, "index":i})


        # SUBTRACT THE COIN AMOUNT WHICH IS SPENT BEFORE
        for key, value in self.allTransactions.items():
            inputs = self.allTransactions[key]["content"]["inputs"]
            for input in inputs:
                for outputTxIdIndexPair in outputTxIdIndex:
                    if input == outputTxIdIndex:
                        totalInputAmount -= \
                            self.allTransactions[input["id"]]["content"]["outputs"][input["index"]]["amount"]

        for key, value in self.pendingTransactions.items():
            for output in self.pendingTransactions[key]["content"]["outputs"]:
                if output["receiver"] == self.currentKey["public"]:
                    pending += output["amount"]

            for input in self.pendingTransactions[key]["content"]["inputs"]:
                if self.allTransactions[input["id"]]["content"]["outputs"][input["index"]]["receiver"] == \
                        self.currentKey["public"]:
                    pending -= self.allTransactions[input["id"]]["content"]["outputs"][input["index"]]["amount"]

        if pending < 0:
            spendableCoin = totalInputAmount + pending
        else:
            spendableCoin = totalInputAmount

        return {"pending": pending, "spendable": spendableCoin}