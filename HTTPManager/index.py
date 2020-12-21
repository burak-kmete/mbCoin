from flask import Flask, jsonify, request


class HTTPManager:
    def __init__(self, server):
        self.server = server
        self.app = Flask(__name__)
        self.setAPIRoutes()
        self.setHomePage()

    def returnHomePageHTML(self):
        with open("./HTTPManager/HomePage.html") as f:
            fileString = f.read() % ("'http://127.0.0.1:" + str(5000 + self.server.myNodeId) + "'")
            f.close()
            return fileString

    def setHomePage(self):
        self.app.add_url_rule("/", "home", self.returnHomePageHTML)
        self.app.run(host="127.0.0.1", port=5000 + self.server.myNodeId)

    def setAPIRoutes(self):
        @self.app.route("/api/createkey", methods=["POST"])
        def createKey():
            data = {'key': request.json["name"]}
            return jsonify(data), 200

        @self.app.route("/api/selectaccount", methods=["POST"])
        def selectAccount():
            data = {'account': request.json["account"]}
            return jsonify(data), 200

        @self.app.route("/api/getbalance", methods=["POST"])
        def getBalance():
            data = {'balance': self.server.myNodeId}
            return jsonify(data), 200

        @self.app.route("/api/maketransaction", methods=["POST"])
        def makeTransaction():
            data = {'fee': request.json["fee"], 'amount': request.json["amount"],
                    'destination': request.json["destination"]}
            return jsonify(data), 200

        @self.app.route("/api/transactionlist", methods=["POST"])
        def transactionList():
            data = {'list': self.server.myNodeId}
            return jsonify(data), 200

        @self.app.route("/api/showprivate", methods=["POST"])
        def showPrivateKey():
            data = {'priv': self.server.myNodeId}
            return jsonify(data), 200
