from HTTPManager.index import HTTPManager
from BlockchainManager.index import BlockchainManager


class Server:
    def __init__(self, myNodeId):
        self.myNodeId = myNodeId
        self.httpManager = None
        self.blockchainManager = None
        self.socketManager = None

    def setManagers(self):
        self.createBlockchainManager()
        self.createHttpManager()
        self.createSocketManager()

    def createHttpManager(self):
        self.httpManager = HTTPManager(self)

    def createBlockchainManager(self):
        self.blockchainManager = BlockchainManager(self.myNodeId)

        pass

    def createSocketManager(self):
        pass