#-*- coding=utf-8 -*-
from flask import render_template, request, session, jsonify
import os

from . import download_routers,upload_routers,index_routers

def init_app(app):
    index_routers.init_app(app)
    download_routers.init_app(app)
    upload_routers.init_app(app)



