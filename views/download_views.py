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

#不验证下载task的view用于测试文件下载
def api_free_download_view():
    key = request.args.get('key', '0')

    if not db.is_download_file_by_key(key):
        return jsonify({'status':'error','error_message':'not exist'}), status.HTTP_404_NOT_FOUND

    if db.is_key_contents_in_merge_status(key):
        clip_list = db.get_clip_upload_status_list_of_key(key)
        return _download_unmerged_content_of_key(key, clip_list)
    else:
        return _download_merged_content_of_key(key)


def api_download_view():
    key = request.args.get('key','0')
    task = request.args.get('task','0')

    if not db.is_download_file_by_key(key):
        return jsonify({'status':'error','error_message':'not exist'}), status.HTTP_404_NOT_FOUND

    if not db.is_download_task_valid(key,task):
        return jsonify({'status':'error'}), status.HTTP_403_FORBIDDEN

    if db.is_key_contents_in_merge_status(key):
        clip_list = db.get_clip_upload_status_list_of_key(key)
        return _download_unmerged_content_of_key(key, clip_list)
    else:
        return _download_merged_content_of_key(key)

#处理还在合并过程中的文件，要进行复杂的异常处理
def _download_unmerged_content_of_key(key, clip_list):
    try:
        content_generate = store.get_merging_content_generate_of_key_and_clipinforamtion(key, clip_list)
        response = Response(stream_with_context(content_generate))
        header = 'attachment; filename='+key
        response.headers["Content-Disposition"] = header
        #response.headers.add('Accept-Ranges', 'bytes')
        return response

    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({'status':'error'}), status.HTTP_404_NOT_FOUND

#返回已经合并过的文件，该过程比较简单，直接读文件即可
def _download_merged_content_of_key(key):
    try:
        content_generate = store.get_content_generate_of_key(key)
        response = Response(stream_with_context(content_generate))
        header = 'attachment; filename='+key
        response.headers["Content-Disposition"] = header
        #response.headers.add('Accept-Ranges', 'bytes')
        return response

    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({'status':'error'}), status.HTTP_404_NOT_FOUND