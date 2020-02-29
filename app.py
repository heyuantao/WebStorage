#-*- coding=utf-8 -*-

from flask import Flask, render_template, request, session, jsonify
from flask_cors import CORS
import os


def create_app():
    app = Flask(__name__,static_folder="./templates/mystorageapp/build/static", template_folder="./templates/mystorageapp/build")
    CORS(app)
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

    from . import routes
    routes.init_app(app)

    return app



if __name__ == '__main__':
    app = create_app()
    app.run(port=34567,host="0.0.0.0")
