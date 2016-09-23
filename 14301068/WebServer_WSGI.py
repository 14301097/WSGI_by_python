# coding=utf-8
# Author:paukey
# Date:2016-9-20
# python 2.7


"""
写个WSGI(Web Server Gateway Interface)，支持主流Python的web框架
http://www.letiantian.me/2015-09-10-understand-python-wsgi/
http://www.rapospectre.com/blog/32
"""

from __future__ import unicode_literals

import socket
import StringIO
import sys
import datetime


class WSGIServer(object):
    socket_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 10

    def __init__(self, server_address):
        # Create a listening socket
        self.socket = socket.socket(self.socket_family, self.socket_type)
        # Allow to reuse the same address
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind
        self.socket.bind(server_address)
        # Activate
        self.socket.listen(self.request_queue_size)
        # Get server host name and port
        host = self.socket.getsockname()[:2]
        self.host = host
        self.port = port

    def set_app(self, app):
        self.app = application

    def serve_forever(self):
        while True:
            # New client connection
            self.connection, client_address = self.socket.accept()
            # Handle one request and close the client connection.
            # Then loop over to wait for another client connection.
            self.handle_request()

    def handle_request(self):
        self.request_data = request_data = self.connection.recv(1024)
        # Print formatted request data a la 'curl -v'
        print(''.join(
            '< {line}\n'.format(line=line)
            for line in request_data.splitlines()
        ))

        self.parse_request(request_data)

        # Construct environment dictionary using request data
        env = self.get_environ()

        # It's time to call our application callable and get
        # back a result that will become HTTP response body
        result = self.app(env, self.start_response)

        # Construct a response and send it back to the client
        self.finish_response(result)

    def parse_request(self, text):
        request_line = text.splitlines()[0]
        request_line = request_line.rstrip('\r\n')
        # Break down the request line into components
        (self.request_method,  # GET
         self.path,  # /hello
         self.request_version  # HTTP/1.1
         ) = request_line.split()

    def get_environ(self):
        env = {}
        # Required WSGI variables
        env['wsgi.version'] = (1, 0)
        env['wsgi.url_scheme'] = 'http'
        env['wsgi.input'] = StringIO.StringIO(self.request_data)
        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once'] = False
        # Required CGI variables
        env['REQUEST_METHOD'] = self.request_method  # GET
        env['PATH_INFO'] = self.path  # /hello
        env['SERVER_NAME'] = self.host  # localhost
        env['SERVER_PORT'] = str(self.port)  # 3333
        return env

    def start_response(self, status, response_headers):
        headers = [
            ('Date', datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')),
            ('Server', 'WSGI0.2'),
        ]
        self.headers_set = [status, response_headers + headers]

    def finish_response(self, app_data):
        try:
            response = 'HTTP/1.1 {status}\r\n'.format(status=self.status)
            for header in self.headers_set:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            for data in app_data:
                response += data
            self.connection.sendall(response)
        finally:
            self.connection.close()


if __name__ == '__main__':
    port = 3333
    if len(sys.argv) < 2:
        sys.exit('请提供可用的wsgi应用程序, 格式为: 模块名.应用名')
    elif len(sys.argv) > 2:
        port = sys.argv[2]


    def generate_server(address, app):
        server = WSGIServer(address)
        server.set_app(app)
        return server


    app_path = sys.argv[1]
    module, app = app_path.split('.')
    module = __import__(module)
    application = getattr(module, app)
    httpd = generate_server(('', int(port)), app)
    print
    'WSGI Server Serving HTTP service on port {0}'.format(port)
    print
    '{0}'.format(datetime.datetime.now().
                 strftime('%a, %d %b %Y %H:%M:%S GMT'))
    httpd.serve_forever()
