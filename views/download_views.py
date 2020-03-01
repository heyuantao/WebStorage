#-*- coding=utf-8 -*-
from flask import render_template, request, session, jsonify, current_app, stream_with_context, Response
from config import config
import os


def api_download_info_view():
    key = request.json.get('key')
    return jsonify({'key':key,'exist':False})


def api_download_url_view():
    key = request.json.get('key')
    return jsonify({'key': key, 'exist': False, 'url':'http://127.0.0.1/abc.zip'})


def api_download_view():
    key = request.args.get('key')
    print("this is key")
    print(key)
    def generate():
        i=1
        while True:
            if i>1000000:
                break
            i=i+1
            yield "sdffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffsdfffffffffffffffffffffffffffffffffffff"

    response = Response(stream_with_context(generate()))
    header = 'attachment; filename='+key
    response.headers["Content-Disposition"] = header
    return response
