import flask
import os
from Server.index import Server
import json

def createFolderStructure():
    if not os.path.exists('./NodeInfoFolder'):
        os.makedirs('./NodeInfoFolder')
        os.makedirs('./NodeInfoFolder/1')
        os.makedirs('./NodeInfoFolder/2')
        os.makedirs('./NodeInfoFolder/3')
        os.makedirs('./NodeInfoFolder/4')
        os.makedirs('./NodeInfoFolder/5')

        i = 1
        while i < 6:
            with open("./NodeInfoFolder/" + str(i) + "/transactions.json", "w") as f:
                json.dump({}, f)
                f.close()
            with open("./NodeInfoFolder/" + str(i) + "/blocks.json", "w") as f:
                json.dump({"blocks": list()}, f)
                f.close()
            with open("./NodeInfoFolder/" + str(i) + "/keys.json", "w") as f:
                json.dump({"keys": list()}, f)
                f.close()
            i += 1

def main():
    #  if folders are not exist, create
    createFolderStructure()

    #  take an id to know which node it is (integer between 1-5)
    myNodeId = ""
    while type(myNodeId) != int or myNodeId > 5 or myNodeId < 1:
        try:
            myNodeId = int(input("Please enter the Node no(integer between 1-5): "))
        except ValueError as e:
            print(e)

    #  create and run the server
    server = Server(myNodeId)
    server.setManagers()


if __name__ == '__main__':
    main()
