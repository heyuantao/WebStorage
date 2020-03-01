#-*- coding=utf-8 -*-
from flask import render_template, request, session, jsonify
from views.download_views import api_download_info_view,api_download_url_view,api_download_view
from views.upload_views import api_upload_view, api_upload_success_view, api_upload_token_view

class Route:

    def init_app(self, app=None, auth=None):
        @app.route('/', methods=['GET', ])
        def index():
            return render_template('index.html')


        @app.route('/api/download/info/', methods=['POST'])     #获取文件信息
        @auth.login_required
        def api_download_info():
            return api_download_info_view()

        @app.route('/api/download/url/', methods=['POST'])     #获取文件的下载链接
        @auth.login_required
        def api_download_url():
            return api_download_url_view()

        @app.route('/api/download/content', methods=['GET',])  #下载文件
        def api_download_key():
            return api_download_view()



        @app.route('/api/upload/', methods=['POST'])
        def api_upload():  # 一个分片上传后被调用
            return api_upload_view()

        @app.route('/api/upload/success/', methods=['POST'])
        def api_upload_success():  # 所有分片均上传完后被调用
            return api_upload_success_view()


        @app.route('/api/upload/token/', methods=['POST'])
        @auth.login_required
        def upload_token():
            return api_upload_token_view()

