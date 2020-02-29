#-*- coding=utf-8 -*-
from flask import render_template, request, session, jsonify
import os

def init_app(app):

    @app.route('/api/upload/', methods=['POST'])
    def upload():  # 一个分片上传后被调用
        upload_file = request.files['file']
        session['real_filename'] = upload_file.filename
        print(session['real_filename'])
        task = request.form.get('task_id')  # 获取文件唯一标识符
        print(task)
        chunk = request.form.get('chunk', 0)  # 获取该分片在所有分片中的序号
        filename = '%s%s' % (task, chunk)  # 构成该分片唯一标识符
        print(filename)
        upload_file.save('upload/%s' % filename)  # 保存分片到本地
        return jsonify({'status': 'sucess', 'mode': 'clip'})

    @app.route('/api/upload/success', methods=['POST'])
    def upload_success():  # 所有分片均上传完后被调用
        task = request.json.get('task_id')
        ext = request.json.get('ext', '')
        upload_type = request.json.get('type')
        if len(ext) == 0 and upload_type:
            ext = upload_type.split('/')[1]
        ext = '' if len(ext) == 0 else '.%s' % ext  # 构建文件后缀名
        chunk = 0
        # saved_filename = session['real_filename']
        saved_filename = "upload.iso"
        print("Saved Filename {}".format(saved_filename))
        with open('upload/%s' % (saved_filename), 'wb') as target_file:  # 创建新文件
            while True:
                try:
                    filename = 'upload/%s%d' % (task, chunk)
                    source_file = open(filename, 'rb')  # 按序打开每个分片
                    target_file.write(source_file.read())
                    source_file.close()
                except IOError:
                    break
                chunk += 1
                os.remove(filename)  # 删除该分片，节约空间
        # return render_template('index.html')
        return jsonify({'status': 'sucess'})

    @app.route('/api/upload/token/', methods=['POST', 'GET'])
    def upload_token():
        return "this is token"
