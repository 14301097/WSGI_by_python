# coding=utf-8
# Author:paukey
# Date:2016-9-22
# python 2.7

from flask import Flask
from flask import Response

flask_app = Flask('flaskapp')


@flask_app.route('/hello')
def hello_world():
    return Response('Hello world from Flask\n', mimetype='text, plain')


app = flask_app.wsgi_app
