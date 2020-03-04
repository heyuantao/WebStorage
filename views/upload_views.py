#-*- coding=utf-8 -*-
from flask import request, jsonify, current_app
from flask_api import status
from config import config
import logging

from db import Database
from storage import Storage
from task import merge_file_by_key_in_celery


logger = logging.getLogger(__name__)

db = Database()
store = Storage()

def api_upload_view():  # 一个分片上传后被调用
    TMP_UPLOAD_PATH = config.FileStorage.TMP_UPLOAD_PATH

    task = request.form.get('task')  # 获取文件唯一标识符
    key = request.form.get('key')
    logger.debug("Key is {} and Task is {} in post to upload api".format(key, task))

    if not db.is_upload_task_valid(key,task):
        return jsonify({'status':'error'}),status.HTTP_403_FORBIDDEN

    upload_file_clip = request.files['file']            #real_filename = upload_file.filename

    chunk = request.form.get('chunk', 0)                # 获取该分片在所有分片中的序号
    filename = '%s%s' % (key, chunk)                    # 构成该分片唯一标识符

    #upload_file.save(TMP_UPLOAD_PATH+'/%s' % filename)  # 保存分片到本地
    store.save_clip(upload_file_clip, key, chunk)
    db.append_clip_upload_partial_status_of_key(key,filename)

    return jsonify({'status': 'sucess', 'mode': 'clip'}), status.HTTP_200_OK


def api_upload_success_view():  # 所有分片均上传完后被调用
    TMP_UPLOAD_PATH = config.FileStorage.TMP_UPLOAD_PATH
    UPLOAD_PATH = config.FileStorage.UPLOAD_PATH

    key = request.json.get('key')
    task = request.json.get('task')

    logger.debug("Key is {} and Task is {} in post to success api".format(key, task))

    if not db.is_upload_task_valid(key,task):
        return jsonify({'status': 'error'}), status.HTTP_403_FORBIDDEN

    ext = request.json.get('ext', '')
    upload_type = request.json.get('type')
    if len(ext) == 0 and upload_type:
        ext = upload_type.split('/')[1]
    ext = '' if len(ext) == 0 else '.%s' % ext  # 构建文件后缀名


    saved_filename = key
    logger.debug("Saved Filename {}".format(saved_filename))

    db.append_clip_upload_success_status_of_key(key)
    clip_count = db.get_clip_upload_status_list_length_of_key(key)


    #如果分片数量不超过4(20M)，程序立刻进行合并分片。如果分片数量过多，则有异步进程进行合并
    if(clip_count<=4):
        print("Clip count for key \"{}\" is \"{}\" merge immediately !".format(key, clip_count))
        store.merge_clip_of_key(key)
        db.clear_clip_upload_status_list_of_key(key)
        db.add_to_downloadable_file_list_by_key(key)
    else:
        print("Clip count for key \"{}\" is \"{}\" merge slowly !".format(key, clip_count))
        merge_file_by_key_in_celery.delay(key)
        #db.clear_clip_upload_status_list_of_key(key) #call in async task #文件在合并的时候，依然可以下载
        db.add_to_downloadable_file_list_by_key(key)

    return jsonify({'status': 'sucess'}), status.HTTP_200_OK

def api_upload_token_view():
    key = request.json.get('key')

    task= db.get_upload_task_by_key(key)
    token_dict = {"key":key,"task":task}

    return jsonify(token_dict)