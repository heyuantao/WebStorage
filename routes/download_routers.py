#-*- coding=utf-8 -*-
from flask import render_template, request, session, jsonify
import os

def init_app(app):
    @app.route('/api/download/info/', methods=['POST', 'GET'])
    def download_info():
        return "this is file info"