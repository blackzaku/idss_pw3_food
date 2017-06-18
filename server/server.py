#!/usr/bin/env python

import http.server
import socketserver
import json

from cgi import parse_header, parse_multipart
from urllib.parse import parse_qs

import sys
sys.path.append("../")
import IdssFood
idss = IdssFood.IdssFood()

class IDSSHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def _set_headers_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()

    def parse_POST(self):
        cthead = self.headers['content-type']
        print(cthead)
        if cthead is not None:
            ctype, pdict = parse_header(cthead)
            if ctype == 'multipart/form-data':
                print(self.rfile)
                postvars = parse_multipart(self.rfile, pdict)
            elif ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers['content-length'])
                data = self.rfile.read(length)
                try:
                    postvars = json.loads(data)
                except ValueError:
                    postvars = parse_qs(data, keep_blank_values=True)
                    pass
            else:
                postvars = {}
        else:
            postvars = {}
        return postvars

    def do_POST(self):
        if self.path == '/suggest':
            parameters = self.parse_POST()

            print(parameters)

            if 'likes' in parameters and 'dislikes' in parameters:
                idss.set_liked(parameters['likes'], parameters['dislikes'])
            if 'ingredients' in parameters and 'no_ingredients' in parameters:
                idss.set_ingredients(parameters["ingredients"], parameters["no_ingredients"])
            if 'labels' in parameters and 'no_labels' in parameters:
                idss.set_labels(parameters["labels"], parameters["no_labels"])

            recommendation = idss.get_recommendation()
            self._set_headers_POST()
            dumped = json.dumps(recommendation)
            self.wfile.write(bytes(dumped, 'utf-8'))
        else:
            return http.server.SimpleHTTPRequestHandler.do_POST(self)

Handler = IDSSHandler

server = socketserver.TCPServer(('0.0.0.0', 8080), Handler)

server.serve_forever()
