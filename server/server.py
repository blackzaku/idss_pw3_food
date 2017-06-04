#!/usr/bin/env python

import http.server
import socketserver

class IDSSHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

Handler = IDSSHandler

server = socketserver.TCPServer(('0.0.0.0', 8080), Handler)

server.serve_forever()