#-*- coding=utf-8 -*-
from flask import render_template, request, session, jsonify, current_app, stream_with_context, Response
from flask_api import status
import traceback
from config import config
from db import Database
from storage import Storage
import os
import logging

logger = logging.getLogger(__name__)

db = Database()
store = Storage()

def api_download_info_view():
    key = request.json.get('key')
    return jsonify({'key':key,'exist':False})


def api_download_url_view():
    key = request.json.get('key')
    task = db.get_download_task_by_key(key)
    site_url = config.App.SITE_URL
    api_url = "/api/download/content"
    download_url = "{0}{1}?key={2}&task={3}".format(site_url,api_url,key,task)
    return jsonify({'key': key, 'url':download_url})


def api_download_view():
    key = request.args.get('key','0')
    task = request.args.get('task','0')

    if not db.is_download_task_valid(key,task):
        return jsonify({'error':'invalid'}), status.HTTP_403_FORBIDDEN

    try:
        content_generate = store.get_key_content_generate(key)
        response = Response(stream_with_context(content_generate))
        header = 'attachment; filename='+key
        response.headers["Content-Disposition"] = header
        return response

    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({'error':'invalid'}), status.HTTP_404_NOT_FOUND

