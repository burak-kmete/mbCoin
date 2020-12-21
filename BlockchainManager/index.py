class BlockchainManager:
    def __init__(self):
        self.currentKeys = {"private": None, "public": None}
        self.minimumFee = 0.5

    def getBalance(self):
        pass

    def setKeys(self, publicKey):
        pass

    def createNewKey(self):
        pass

    def makeTransaction(self, fee, amount, destination):
        pass

    def getBestBlock(self):
        pass
