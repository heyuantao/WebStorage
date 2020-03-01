#-*- coding=utf-8 -*-
from flask import render_template, request, session, jsonify, current_app
import os


def api_download_key_info_view():
    settings = current_app.config
    return jsonify(settings['UPLOAD_PATH'])


def api_download_key_privateurl_view():
    return "not implement"


def api_download_key_view():
    return "not implement"
