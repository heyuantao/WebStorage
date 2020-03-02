#-*- coding=utf-8 -*-
from flask import render_template, request, session, jsonify, current_app
from random import random
from uuid import uuid4
from config import config
import os


def api_upload_view():  # 一个分片上传后被调用
    TMP_UPLOAD_PATH = config.FileStorage.TMP_UPLOAD_PATH

    upload_file = request.files['file']
    session['real_filename'] = upload_file.filename
    print(session['real_filename'])
    task = request.form.get('task')  # 获取文件唯一标识符
    key = request.form.get('key')
    print("Task is {} key is {} in post to upload api".format(task, key))
    chunk = request.form.get('chunk', 0)  # 获取该分片在所有分片中的序号
    filename = '%s%s' % (key, chunk)  # 构成该分片唯一标识符
    print(filename)
    upload_file.save(TMP_UPLOAD_PATH+'/%s' % filename)  # 保存分片到本地
    return jsonify({'status': 'sucess', 'mode': 'clip'})


def api_upload_success_view():  # 所有分片均上传完后被调用
    TMP_UPLOAD_PATH = config.FileStorage.TMP_UPLOAD_PATH
    UPLOAD_PATH = config.FileStorage.UPLOAD_PATH

    task = request.json.get('task')
    key = request.json.get('key')
    print("Task is {} key is {} in post to success api".format(task, key))
    ext = request.json.get('ext', '')
    upload_type = request.json.get('type')
    if len(ext) == 0 and upload_type:
        ext = upload_type.split('/')[1]
    ext = '' if len(ext) == 0 else '.%s' % ext  # 构建文件后缀名
    chunk = 0

    saved_filename = "upload.iso"
    print("Saved Filename {}".format(saved_filename))
    with open(UPLOAD_PATH+'/%s' % (saved_filename), 'wb') as target_file:  # 创建新文件
        while True:
            try:
                filename = TMP_UPLOAD_PATH+'/%s%d' % (key, chunk)
                source_file = open(filename, 'rb')  # 按序打开每个分片
                target_file.write(source_file.read())
                source_file.close()
            except IOError:
                break
            chunk += 1
            os.remove(filename)  # 删除该分片，节约空间
    return jsonify({'status': 'sucess'})

def api_upload_token_view():
    task = uuid4().hex
    token_dict = {"key":"absdfdsfds.zip","task":task}
    return jsonify(token_dict)