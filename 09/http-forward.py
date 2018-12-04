import http.client
import http.server
import sys
import urllib.request
import json
import socket
from urllib.error import HTTPError, URLError


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # print("calling get")
        headers = dict(self.headers)
        # TODO: remove these 2 lines when pushing
        # if 'Host' in headers:
        #   del headers['Host']
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Connection", "close")
        self.end_headers()
        request = urllib.request.Request(headers=headers, url='http://' + upstream, method="GET")
        self.wfile.write(bytes(
            json.dumps(
                self.contactUpstream(request),
                ensure_ascii=False,
                indent=4
            ), 'UTF-8'
        ))

    def do_POST(self):
        # print("calling post")
        outJson = None
        content_len = int(self.headers.get('content-length', 0))
        content = self.rfile.read(content_len)
        # print(content)
        requestContents = None

        try:
            requestContents = json.loads(content)
        except:
            pass

        if requestContents is None or \
                (requestContents["type"] == "POST"
                 and ("url" not in requestContents or "content" not in requestContents)
                ):
            outJson = {"code": "invalid json"}

        else:
            headers = dict(self.headers)
            if 'headers' in requestContents:
                headers = dict(requestContents['headers'])
            # TODO: remove these 2 lines when pushing
            # if 'Host' in headers:
            #     del headers['Host']

            # print('headers {}'.format(headers))
            sentReq = urllib.request.Request(
                url=requestContents["url"],
                data=requestContents["content"].encode("utf-8"),
                headers=headers,
                method=requestContents["type"] if "type" in requestContents else "GET"
            )

            timeout = 1
            if 'timeout' in requestContents:
                timeout = requestContents['timeout']

            # print('timeout {}'.format(timeout))
            try:
                response = urllib.request.urlopen(sentReq, timeout=timeout)
                outJson = self.parseResponseFromUpstream(
                    response.status,
                    dict(response.getheaders()),
                    response.read()
                )

            except URLError:
                # return json timeout
                outJson = {"code": "timeout"}
            except socket.timeout:
                # return json timeout
                outJson = {"code": "timeout"}

            # print('out json {}'.format(outJson))
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(outJson, ensure_ascii=False, indent=4), 'UTF-8'))
        return

    def contactUpstream(self, request):
        try:
            with urllib.request.urlopen(request, timeout=1) as response:
                return self.parseResponseFromUpstream(
                    response.status,
                    dict(response.getheaders()),
                    response.read()
                )

        except socket.timeout:
            # return json timeout
            return {"code": "timeout"}

    def parseResponseFromUpstream(
            self,
            responseHttpCode,
            responseHttpHeaders,
            responseContent
    ):
        respEncoded = {"code": responseHttpCode, "headers": responseHttpHeaders}
        try:
            respEncoded["json"] = json.loads(responseContent)
        except:
            respEncoded["json"] = responseContent
        return respEncoded


port = sys.argv[1]
upstream = sys.argv[2]


def run(port, server_class=http.server.HTTPServer, handler_class=RequestHandler):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


run(int(port))