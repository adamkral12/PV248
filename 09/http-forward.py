import http.client
import http.server
import json
import sys
import socket


def urlBlocks(url):
    if "/" not in url:
        return url, ""
    if "//" in url:
        blocks = url.split("/", 3)
        return blocks[2], "/" + blocks[3]
    else:
        blocks = url.split("/", 1)
        return blocks[0], "/" + blocks[1]


def isParseableJson(jsonValue):
    try:
        json.loads(jsonValue)
    except ValueError:
        return False
    return True


class HTTPHandler(http.server.BaseHTTPRequestHandler):
    def sendResponse(self, dic):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(dic).encode()))

    def do_GET(self):
        client = http.client.HTTPConnection(urlBlocks(str(sys.argv[2]))[0], timeout=1)
        try:
            client.request(
                "GET",
                urlBlocks(str(sys.argv[2]))[1],
                None,
                self.headers
            )
        except socket.timeout:
            self.sendResponse({"code": "timeout"})
        else:
            resp = dict()
            clientResponse = client.getresponse()
            resp["headers"] = clientResponse.getheaders()
            resp["code"] = clientResponse.getcode()
            body = clientResponse.read()
            try:
                decoded = isParseableJson(body.decode())
            except UnicodeDecodeError:
                resp["content"] = str(body)
            else:
                if decoded:
                    resp["json"] = json.loads(body.decode())
                else:
                    resp["content"] = str(body.decode())
            self.sendResponse(resp)

    def do_POST(self):
        data = self.rfile.read(int(self.headers.get('content-length', 0)))
        try:
            jsonData = json.loads(data)
        except ValueError:
            self.sendResponse({"code": "invalid json"})
            return
        if "url" not in jsonData.keys() or \
                ("type" in jsonData.keys() and
                 jsonData["type"] == "POST" and
                 "content" not in jsonData.keys()):

            self.sendResponse({"code": "invalid json"})
            return
        if "timeout" in jsonData.keys():
            timeout = jsonData["timeout"]
        else:
            timeout = 1

        if "type" in jsonData.keys() and jsonData["type"] == "POST":
            body = jsonData["content"]
        else:
            body = None

        if not isinstance(body, str) and body is not None:
            body = json.dumps(body)

        if "headers" in jsonData.keys():
            headers = jsonData["headers"]
        else:
            headers = dict()

        client = http.client.HTTPConnection(urlBlocks(jsonData["url"])[0], timeout=timeout)

        try:
            client.request(jsonData["type"], urlBlocks(jsonData["url"])[1], body, headers)
        except socket.timeout:
            self.sendResponse({"code": "timeout"})
        else:
            resp = dict()
            clientResponse = client.getresponse()
            resp["code"] = clientResponse.getcode()
            resp["headers"] = clientResponse.getheaders()
            body = clientResponse.read()
            try:
                decoded = isParseableJson(body.decode())
            except UnicodeDecodeError:
                resp["content"] = str(body)
            else:
                if decoded:
                    resp["json"] = json.loads(body.decode())
                else:
                    resp["content"] = str(body.decode())
            self.sendResponse(resp)


port = int(sys.argv[1])
server = http.server.HTTPServer(("", port), HTTPHandler)
server.serve_forever()
