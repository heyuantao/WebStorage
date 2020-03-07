#-*- coding=utf-8 -*-
from flask import request, jsonify, current_app, stream_with_context, Response
from flask_api import status
from werkzeug.urls import url_quote
import urllib.parse
import base64
import traceback
from config import config
from db import Database
from storage import Storage
import logging

logger = logging.getLogger(__name__)

db = Database()
store = Storage()

def api_file_info_view():
    key = request.json.get('key')
    return jsonify({'key':key,'exist':False})


def api_file_url_view():
    key = request.json.get('key','0')
    realname = request.json.get('realname','0')
    if realname=='0':
        realname=key
    task = db.get_download_task_by_key(key,realname)
    #site_url = config.App.SITE_URL
    site_url = "http://"+request.headers.get('host')
    api_url = "/file/content"
    #download_url = "{0}{1}?key={2}&task={3}".format(site_url, api_url, base64.b64encode(urllib.parse.quote(key).encode("utf-8")).decode(), task) #urllib.parse.quote(key)
    download_url = "{0}{1}?key={2}&task={3}".format(site_url, api_url, key, task) #urllib.parse.quote(key)

    return jsonify({'key': key, 'url':download_url})

#不验证下载task的view用于测试文件下载,该接口为测试接口
def file_freecontent_view():
    key = request.args.get('key', '0')
    #key = base64.urlsafe_b64decode(raw_key).decode("utf-8")
    #key = urllib.parse.unquote_plus(request.args.get('key', '0'))
    #print(key)
    if not db.is_download_file_by_key(key):
        return jsonify({'status':'error','error_message':'not exist'}), status.HTTP_404_NOT_FOUND

    if db.is_key_contents_in_merge_status(key):
        clip_list = db.get_clip_upload_status_list_of_key(key)
        return _download_unmerged_content_of_key(key, clip_list)
    else:
        return _download_merged_content_of_key(key)


def file_content_view():
    key = request.args.get('key', '0')

    '''
    other_key =raw_key.encode('utf-8').decode()
    print(type(other_key))
    print(other_key)
    other2_key = base64.b64decode(other_key).decode()
    other3_key = urllib.parse.unquote(other2_key)
    key=other3_key
    '''

    task = request.args.get('task','0')

    if not db.is_download_file_by_key(key):
        return jsonify({'status':'error','error_message':'not exist'}), status.HTTP_404_NOT_FOUND

    if not db.is_download_task_valid(key,task):
        return jsonify({'status':'error','error_message':'invalid'}), status.HTTP_403_FORBIDDEN

    realname = db.get_download_realname_by_key(key)

    if db.is_key_contents_in_merge_status(key):
        clip_list = db.get_clip_upload_status_list_of_key(key)
        return _download_unmerged_content_of_key(key, realname, clip_list)
    else:
        return _download_merged_content_of_key(key,realname)

#处理还在合并过程中的文件，要进行复杂的异常处理
def _download_unmerged_content_of_key(key, realname, clip_list):
    try:
        content_generate = store.get_merging_content_generate_of_key_and_clipinforamtion(key, clip_list)
        file_size = store.get_merging_content_size_of_key(key, clip_list)
        #response = Response(stream_with_context(content_generate))
        response = Response(content_generate, content_type="application/octet-stream")
        #header = 'attachment; filename='+url_quote(key)
        header = 'attachment; filename=' + url_quote(realname)
        response.headers["Content-Disposition"] = header
        #response.headers.add('Accept-Ranges', 'bytes')
        response.headers['content-length'] = file_size
        return response

    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({'status':'error'}), status.HTTP_404_NOT_FOUND

#返回已经合并过的文件，该过程比较简单，直接读文件即可
def _download_merged_content_of_key(key, realname):
    try:
        content_generate = store.get_content_generate_of_key(key)
        file_size = store.get_content_size_of_key(key)
        #response = Response(stream_with_context(content_generate))
        response = Response(content_generate, content_type="application/octet-stream")
        #header = 'attachment; filename='+url_quote(key)
        header = 'attachment; filename=' + url_quote(realname)
        #headers['content-length'] = os.stat(str(file_path)).st_size
        response.headers["Content-Disposition"] = header
        response.headers['content-length'] = file_size

        return response

    except Exception as e:
        logger.error(traceback.format_exc())
        return jsonify({'status':'error'}), status.HTTP_404_NOT_FOUND