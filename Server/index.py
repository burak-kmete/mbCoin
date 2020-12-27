from HTTPManager.index import HTTPManager
from BlockchainManager.index import BlockchainManager
from SocketManager.index import SocketManager
import threading


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
        th = threading.Thread(target=self.httpManagerThreadFunction)
        th.start()

    def createBlockchainManager(self):
        self.blockchainManager = BlockchainManager(self)

    def createSocketManager(self):
        th = threading.Thread(target=self.socketManagerThreadFunction)
        th.start()

    def httpManagerThreadFunction(self):
        self.httpManager = HTTPManager(self)

    def socketManagerThreadFunction(self):
        self.socketManager = SocketManager(self)
        self.socketManager.startListener()