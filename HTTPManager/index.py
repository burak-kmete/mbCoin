from flask import Flask


class HTTPManager:
    def __init__(self, server):
        self.server = server
        self.app = Flask(__name__)
        self.setHomePage()

    def returnHomePageHTML(self):
        with open("./HTTPManager/HomePage.html") as f:
            fileString = f.read()
            f.close()
            return fileString

    def setHomePage(self):
        self.app.add_url_rule("/", "home", self.returnHomePageHTML)
        self.app.run(host="127.0.0.1", port=5000 + self.server.myNodeId)
