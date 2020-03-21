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
    task = request.form.get('task')  # 获取文件唯一标识符
    key = request.form.get('key')
    logger.debug("Key is {} and Task is {} in post to upload api".format(key, task))

    if not db.is_upload_task_valid(key,task):
        return jsonify({'status':'error'}),status.HTTP_403_FORBIDDEN

    if db.is_exceed_size_limit_of_key(key):
        return jsonify({'status':'error','error_message':'file size limit exceed'}),status.HTTP_400_BAD_REQUEST

    upload_file_clip = request.files['file']            #real_filename = upload_file.filename

    chunk = request.form.get('chunk', 0)                # 获取该分片在所有分片中的序号
    filename = '%s%s' % (key, chunk)                    # 构成该分片唯一标识符

    #upload_file.save(TMP_UPLOAD_PATH+'/%s' % filename)  # 保存分片到本地
    store.save_clip(upload_file_clip, key, chunk)
    #根据上传的分片序号来更新上传任务设置的超时时间，而不是每次都去更新超时时间，即每500M上传后更新一下
    if int(chunk)%100==0:
        db.update_upload_task_expire_time_by_key(key)

    db.append_clip_upload_partial_status_of_key(key,filename)

    return jsonify({'status': 'sucess', 'mode': 'clip'}), status.HTTP_200_OK


def api_upload_success_view():  # 所有分片均上传完后被调用
    key = request.json.get('key')
    task = request.json.get('task')

    logger.debug("Key is {} and Task is {} in post to success api".format(key, task))

    if not db.is_upload_task_valid(key,task):
        return jsonify({'status': 'error'}), status.HTTP_403_FORBIDDEN

    '''
    ext = request.json.get('ext', '')           #当前未使用
    upload_type = request.json.get('type')      #当前未使用

    if len(ext) == 0 and upload_type:           #当前未使用
        ext = upload_type.split('/')[1]
    ext = '' if len(ext) == 0 else '.%s' % ext  # 构建文件后缀名
    '''

    saved_filename = key
    logger.debug("Saved Filename {}".format(saved_filename))
    #append 'success' to clip list and clear token for upload
    db.append_clip_upload_success_status_of_key(key)
    clip_count = db.get_clip_upload_status_list_length_of_key(key)


    #如果分片数量不超过4(20M)，程序立刻进行合并分片。如果分片数量过多，则有异步进程进行合并
    if(clip_count<=4):
        logger.info("Clip count for key \"{}\" is \"{}\" merge immediately !".format(key, clip_count))
        store.merge_clip_of_key(key)
        db.clear_clip_upload_status_list_of_key(key)
        db.add_to_downloadable_file_list_by_key(key)
    else:
        logger.info("Clip count for key \"{}\" is \"{}\" merge slowly !".format(key, clip_count))
        merge_file_by_key_in_celery.delay(key)
        #db.clear_clip_upload_status_list_of_key(key) #call in async task #文件在合并的时候，依然可以下载
        db.add_to_downloadable_file_list_by_key(key)

    return jsonify({'status': 'sucess'}), status.HTTP_200_OK

def api_upload_token_view():
    key = request.json.get('key')
    #size要上传文件的大小上限，用于在上传时进行计算，如果实际上传文件大小超过该值，则中止上传。可以不携带该该参数，默认为-1，表示不限制上传大小
    size = request.json.get('size',-1)
    #检查该key是否已经使用，即在"可下载"和"待删除"列表中
    if db.is_key_occupied(key):
        return jsonify({'status': 'error','error_message':'key is occupied'}), status.HTTP_403_FORBIDDEN

    task= db.get_upload_task_by_key(key,size)
    token_dict = {"key":key,"task":task,"size":size}

    return jsonify(token_dict)

def api_upload_info_view():
    key = request.json.get('key','0')
    task = request.json.get('task','0')
    if key =='0' or task=='0':
        return jsonify({'status': 'error', 'error_message': 'key or task is empty'}), status.HTTP_400_BAD_REQUEST
    result_dict = db.get_upload_info_by_key(key)        #{'task': task, 'size': size}
    task_value = result_dict['task']
    if task_value!=task:
        return jsonify({'status': 'error', 'error_message': 'task is not valid'}), status.HTTP_400_BAD_REQUEST
    return jsonify(result_dict)