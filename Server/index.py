from HTTPManager.index import HTTPManager


class Server:
    def __init__(self, myNodeId):
        self.myNodeId = myNodeId
        self.httpManager = None
        self.blockchainManager = None
        self.socketManager = None

    def setManagers(self):
        self.createHttpManager()
        self.createBlockchainManager()
        self.createSocketManager()

    def createHttpManager(self):
        self.httpManager = HTTPManager(self)

    def createBlockchainManager(self):
        pass

    def createSocketManager(self):
        pass