#-*- coding=utf-8 -*-
from flask import request, jsonify, current_app, stream_with_context, Response
from flask_api import status
import traceback
from config import config
from db import Database
from storage import Storage
import logging

logger = logging.getLogger(__name__)

db = Database()
store = Storage()

def api_file_list_view():
    #key = request.args.get('key','0')
    #if key=='0':
    #    return jsonify({'error': 'invalid'}), status.HTTP_404_NOT_FOUND
    file_list = []
    file_list_in_db_cache = db.get_file_list_cache()
    for item in file_list_in_db_cache:
        file_list.append(item)
    return_json={'files':file_list,'count':len(file_list)}

    return jsonify(return_json)

def api_file_delete_view():
    key = request.json.get('key','0')
    if key=='0':
        return jsonify({'status': 'error'}), status.HTTP_404_NOT_FOUND
    db.delete_downloadable_file_list_by_key(key)
    store.delete_by_key(key)
    return jsonify({'status': 'success'})