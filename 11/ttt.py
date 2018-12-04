import http.server
import sys
from urllib.parse import urlparse
import json


class RequestHandler(http.server.BaseHTTPRequestHandler):
    gameBoards = dict()

    def generateNewId(self):
        if self.gameBoards.__len__() == 0:
            return 1
        return max(self.gameBoards) + 1

    def newBoard(self, id, name):
        self.gameBoards[id] = dict()
        self.gameBoards[id]['name'] = name
        self.gameBoards[id]['board'] = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]

    def getBoardById(self, id):
        return self.gameBoards[id]


    def do_GET(self):
        query = urlparse(self.path).query
        path = urlparse(self.path).path
        query_components = dict(qc.split("=") for qc in query.split("&"))
        print("query components {}".format(query_components))

        if path == '/start':
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Connection", "close")
            self.end_headers()
            gameId = self.generateNewId()
            print("id {}".format(gameId))
            self.newBoard(gameId, query_components['name'])

            print("game boards {}".format(self.gameBoards))
            self.wfile.write(bytes(
                json.dumps(
                    {"id": gameId},
                    ensure_ascii=False,
                    indent=4
                ), 'UTF-8'
            ))

port = sys.argv[1]


def run(port, server_class=http.server.HTTPServer, handler_class=RequestHandler):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


run(int(port))