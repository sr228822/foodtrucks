#!/usr/bin/python

from flask import Flask
from flask import request
app = Flask(__name__)

@app.route('/api/v1/test')
def tasks():
    resp = 'Hello world!'
    args = request.args
    return str(args)

if __name__ == '__main__':
    app.run(debug = True)
