import http.server
import sys
from urllib.parse import urlparse
import json
import copy

class RequestHandler(http.server.BaseHTTPRequestHandler):
    gameBoards = dict()

    def generateNewId(self):
        if self.gameBoards.__len__() == 0:
            return 1
        print('keys {}'.format(self.gameBoards.keys()))
        return max(self.gameBoards) + 1

    def newBoard(self, boardId, name):
        self.gameBoards[boardId] = dict()
        self.gameBoards[boardId]['name'] = name
        self.gameBoards[boardId]['board'] = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        self.gameBoards[boardId]['next'] = 1

    def getBoardById(self, id):
        return self.gameBoards[id]

    def switchToNextPlayer(self, playerNumber):
        if playerNumber == 1:
            return 2
        elif playerNumber == 2:
            return 1
        else:
            raise Exception("Unknown player number {}".format(playerNumber))

    def getNextPlayerNumber(self, gameId):
        if gameId in self.gameBoards:
            return self.gameBoards[gameId]['next']
        else:
            raise Exception("Unknown game board id ".format(gameId))

    def doResponse(self, responseJson):
        self.wfile.write(bytes(
            json.dumps(
                responseJson,
                ensure_ascii=False,
                indent=4
            ), 'UTF-8'
        ))

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
            if 'name' not in query_components:
                outjson = {'error': 'parameter name not provided'}
            else:
                self.newBoard(gameId, query_components['name'])
                outjson = {"id": gameId}

            self.doResponse(outjson)
        elif path == '/status':
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Connection", "close")
            self.end_headers()
            if 'game' not in query_components:
                responseJson = {"error": "parameter game not provided"}
            else:
                boardGameId = int(query_components['game'])
                if boardGameId not in self.gameBoards:
                    responseJson = {"error": "Unknown game board id {}".format(boardGameId)}
                else:
                    copiedGameBoard = copy.deepcopy(self.gameBoards[boardGameId])
                    copiedGameBoard.pop('name')
                    responseJson = copiedGameBoard

            self.doResponse(responseJson)

        print("game boards {}".format(self.gameBoards))

port = sys.argv[1]


def run(port, server_class=http.server.HTTPServer, handler_class=RequestHandler):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


run(int(port))