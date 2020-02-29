#-*- coding=utf-8 -*-
from flask import render_template, request, session, jsonify
import os


def init_app(app):
    @app.route('/', methods=['GET', ])
    def index():
        return render_template('index.html')