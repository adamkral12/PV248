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
        # print('keys {}'.format(self.gameBoards.keys()))
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

    def switchToNextPlayer(self, playerNumber, gameBoardId):
        if playerNumber == 1:
            self.gameBoards[gameBoardId]['next'] = 2
        elif playerNumber == 2:
            self.gameBoards[gameBoardId]['next'] = 1
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

    def sendHeaders(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Connection", "close")
        self.end_headers()

    def formatBadResponse(self, message):
        return {
            "status": "bad",
            "message": message
        }

    def getWinner(self, boardGameId):
        #  Stupid function, not extensible, but it works
        numberOfZeros = 0
        boardGame = self.gameBoards[boardGameId]['board']
        for index, value in enumerate(boardGame):
            if (value[0] == value[1] == value[2]) and value[0] != 0:
                return value[0]

            for index2, value2, in enumerate(value):
                if value2 == 0:
                    numberOfZeros += 1

        transposed = list(zip(*boardGame))

        for index, value in enumerate(transposed):
            if (value[0] == value[1] == value[2]) and value[0] != 0:
                return value[0]
        #     Diagonal
        mid = boardGame[1][1]
        if mid != 0:
            if boardGame[0][0] == boardGame[2][2] == mid:
                return mid

            if boardGame[0][2] == boardGame[2][0] == mid:
                return mid

        # no fields left to plat -> draw
        if numberOfZeros == 0:
            return 0

    def validatePlayParameters(self, gameBoardId, playerNumber, x, y):
        if gameBoardId not in self.gameBoards:
            raise Exception("Unknown game board id {}".format(gameBoardId))
        if playerNumber != self.getNextPlayerNumber(gameBoardId):
            raise Exception("It's not your turn: player number {}".format(playerNumber))
        gameBoard = self.gameBoards[gameBoardId]['board']
        if [index for index, value in enumerate(gameBoard) if index == x].__len__() == 0:
            raise Exception("Invalid board dimension x: {}".format(x))
        if [index for index, value in enumerate(gameBoard[x]) if index == y].__len__() == 0:
            raise Exception("Invalid board dimension y: {}".format(y))
        if gameBoard[x][y] != 0:
            raise Exception("Field {} {} is already taken".format(x, y))

    def do_GET(self):
        query = urlparse(self.path).query
        path = urlparse(self.path).path
        # print("query {}".format(query))
        if not query:
            self.sendHeaders()
            self.doResponse(self.formatBadResponse("parameters not provided"))
            return
        query_components = dict(qc.split("=") for qc in query.split("&"))
        # print("query components {}".format(query_components))
        if path == '/start':
            self.sendHeaders()
            gameId = self.generateNewId()
            # print("id {}".format(gameId))
            if 'name' not in query_components:
                outjson = self.formatBadResponse('parameter name not provided')
            else:
                self.newBoard(gameId, query_components['name'])
                outjson = {"id": gameId}

            self.doResponse(outjson)
            return
        elif path == '/status':
            self.sendHeaders()
            if 'game' not in query_components:
                responseJson = self.formatBadResponse("parameter game not provided")
            else:
                boardGameId = int(query_components['game'])
                if boardGameId not in self.gameBoards:
                    responseJson = self.formatBadResponse("Unknown game board id {}".format(boardGameId))
                else:
                    winner = self.getWinner(boardGameId)
                    if winner is not None:
                        responseJson = {"winner": winner}
                    else:
                        copiedGameBoard = copy.deepcopy(self.gameBoards[boardGameId])
                        copiedGameBoard.pop('name')
                        responseJson = copiedGameBoard

            self.doResponse(responseJson)
            return
        elif path == '/play':
            self.sendHeaders()
            if 'game' not in query_components:
                responseJson = self.formatBadResponse("Parameter game not provided")
            elif 'player' not in query_components:
                responseJson = self.formatBadResponse("Parameter player not provided")
            elif 'x' not in query_components:
                responseJson = self.formatBadResponse("Parameter x not provided")
            elif 'y' not in query_components:
                responseJson = self.formatBadResponse("Parameter y not provided")
            else:
                # params provided
                boardGameId = int(query_components['game'])
                playerNumber = int(query_components['player'])
                x = int(query_components['x'])
                y = int(query_components['y'])
                try:
                    self.validatePlayParameters(
                        boardGameId,
                        playerNumber,
                        x,
                        y
                    )
                    # Params validated
                    winner = self.getWinner(boardGameId)
                    if winner is not None:
                        responseJson = self.formatBadResponse("The game is over, winner {}".format(winner))
                    else:
                        self.gameBoards[boardGameId]['board'][x][y] = playerNumber
                        self.switchToNextPlayer(playerNumber, boardGameId)
                        responseJson = {"status": "ok"}
                except Exception as e:
                    # print("Exception {}".format(e))
                    responseJson = self.formatBadResponse(e.args[0])

            self.doResponse(responseJson)
            return
        # print("game boards {}".format(self.gameBoards))

port = sys.argv[1]


def run(port, server_class=http.server.HTTPServer, handler_class=RequestHandler):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


run(int(port))