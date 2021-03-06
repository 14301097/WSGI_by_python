# coding=utf-8
# Author:paukey
# Date:2016-9-26
# python 2.7

"""
测试以下功能:
1 实现静态文件就如服务器开启之后在网址上输入localhost:8888/hello.html
如果存在就显示文件内容，不存在就显示404Not found
2动态资源输入网址localhost:8888/aaa  返回hello aaa
"""

from __future__ import unicode_literals
import socket
import StringIO
import sys
import datetime
import os


class WSGIServer(object):
    socket_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 10

    def __init__(self, address):
        # Create a listening socket
        self.socket = socket.socket(self.socket_family, self.socket_type)
        # Allow to reuse the same address
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind
        self.socket.bind(address)
        # Activate
        self.socket.listen(self.request_queue_size)
        # Get server host name and port
        host, port = self.socket.getsockname()[:2]
        self.host = host
        self.port = port

    def set_App(self, application):
        self.application = application

    def beginServer(self):
        print "Begin listening..."
        while 1:
            self.connection, address = self.socket.accept()
            self.sendRequest()

    def sendRequest(self):
        self.request_data = self.connection.recv(1024)
        self.request_lines = self.request_data.splitlines()
        try:
            self.getUrl()
            env = self.getEnviron()

            print env['PATH_INFO'][1:]

            if env['PATH_INFO'][1:].endswith(".html"):
                application = 'app1'
            else:
                application = 'app2'

            application = getattr(module, application)
            httpd.setApplication(application)

            app_data = self.application(env, self.startResponse)
            self.finishResponse(app_data)
            print '[{0}] "{1}" {2}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                           self.request_lines[0], self.status)
        except Exception, e:
            pass

    def getUrl(self):
        self.request_dict = {'Path': self.request_lines[0]}
        for itm in self.request_lines[1:]:
            if ':' in itm:
                self.request_dict[itm.split(':')[0]] = itm.split(':')[1]
        self.request_method, self.path, self.request_version = self.request_dict.get('Path').split()

    def getEnviron(self):
        env = {
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': StringIO.StringIO(self.request_data),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'REQUEST_METHOD': self.request_method,
            'PATH_INFO': self.path,
            'SERVER_NAME': self.host,
            'SERVER_PORT': self.port,
            'USER_AGENT': self.request_dict.get('User-Agent')
        }
        return env

    def startResponse(self, status, response_headers):
        headers = [
            ('Date', datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')),
            ('Server', 'WSGI'),
        ]
        self.headers = response_headers + headers
        self.status = status

    def finishResponse(self, app_data):
        try:
            response = 'HTTP/1.1 {status}\r\n'.format(status=self.status)
            for header in self.headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            for data in app_data:
                response += data
            self.connection.sendall(response)
        finally:
            self.connection.close()


def app1(environ, start_response):
    filename = environ['PATH_INFO'][1:]

    if os.path.exists(filename):
        f = open(filename, "r")
        line = f.readline()
        message = line
        while line:
            line = f.readline()
            message = message + line

        status = '200 OK'
        response_headers = [('Content-Type', 'text/plain')]
        start_response(status, response_headers)
        return [message]
    else:
        status = '404 NOT FOUND'
        response_headers = [('Content-Type', 'text/plain')]
        start_response(status, response_headers)
        return ['Can not find the file!']


def app2(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain')]
    start_response(status, response_headers)

    return ['Hello ', environ['PATH_INFO'][1:]]


if __name__ == '__main__':
    httpd = WSGIServer(('', int(8888)))

    print "Web Server start..."

    module = 'WSGIServer'
    module = __import__(module)

    httpd.beginServer()
