import socket
import threading
from constants import Peers
from time import sleep
import json
import sys


class SocketManager:
    def __init__(self, server):
        self.server = server
        self.listenerSocket = None
        self.listenerThread = None
        self.peerNodeIds = Peers["NODE_"+str(self.server.myNodeId)]
        self.createListenerSocket()

    def createListenerSocket(self):
        # Create a TCP/IP socket
        self.listenerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ('localhost', 3000 + self.server.myNodeId)
        print('Starting up on {} port {}'.format(*server_address))
        self.listenerSocket.bind(server_address)

        # Listen for incoming connections
        self.listenerSocket.listen(100)

    def startListener(self):
        self.listenerThread = threading.Thread(target=self.listenerThreadFunction)
        self.listenerThread.start()

    def listenerThreadFunction(self):
        # listen for the new nodes wanting to join
        newPeerSockets = []
        while True:
            # Wait for a connection
            print('waiting for a new peer connection')
            newPeerSockets.append(None)
            newPeerSockets[-1], client_address = self.listenerSocket.accept()
            try:
                print('connection from', client_address)

                # Receive the operation name and the related data to perform this operation
                data = b''
                while True:
                    newDataPiece = newPeerSockets[-1].recv(16)
                    if newDataPiece:
                        data += newDataPiece
                    else:
                        threading.Thread(target=self.handleNewOperationRequest, args=(newPeerSockets[-1], json.loads(data.decode()))).start()
                        break
            except:
                print("PROBLEM OCCURED IN NEW PEER SOCKET CONNECTION!")
                print(sys.exc_info()[0]) #print the error

    def handleNewOperationRequest(self, peerSocket, dataObject):
        newNodeId = dataObject["nodeId"]
        operation = dataObject["operation"]

        print('NodeId of the new connection: ' + str(newNodeId) + ". Operation is: " + str(operation))

        print(str(operation) + " successfully end.")
        peerSocket.close()

    def createOperationThread(self, operation, data):
        print("oepration thread creation function")
        if operation == "test_operation":
            threading.Thread(target=self.testOperation, args=data).start()

        # add other operation threads and set the related operation functions like above


    def testOperation(self, data):
        objectToSend = {"nodeId": self.server.myNodeId, "operation": "testOperation"}

        # lets assume data is another dictionary object
        objectToSend.update({"data": data})

        # convert the dictionary to bytes object to send through socket connection
        bytesData = str.encode(json.dumps(objectToSend))

        # send to all peers
        for peerId in self.peerNodeIds:
            try:
                server_address = ('localhost', 3000 + peerId)
                print('Sending a operation request to NODE_' + str(peerId))
                operationSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                operationSocket.connect(server_address)
                operationSocket.sendall(bytesData)
                print('Sending operation request to NODE_' + str(peerId) + " is successful")

            except ConnectionRefusedError as e:
                print("PROBLEM OCCURED WHILE TRYING TO SEND A OPERATION REQUEST!")
                print ("Connection refused by the NODE_" + str(peerId))

            except:
                print(sys.exc_info()[0])  # print the error
                print("Couldnt connect to the NODE_" + str(peerId))
