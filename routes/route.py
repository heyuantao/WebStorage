#-*- coding=utf-8 -*-
from flask import render_template, request, session, jsonify
from views.download_views import api_download_key_info_view,api_download_key_privateurl_view,api_download_key_view
from views.upload_views import api_upload_view, api_upload_success_view, api_upload_token_view

class Route:
    def init_app(self, app=None, auth=None):
        @app.route('/', methods=['GET', ])
        def index():
            return render_template('index.html')


        @app.route('/api/download/key/info', methods=['GET', ])
        def api_download_key_info():
            return api_download_key_info_view()

        @app.route('/api/download/key/url/', methods=['GET', ])
        def api_download_key_privateurl():
            return api_download_key_privateurl_view()

        @app.route('/api/download/key', methods=['GET', ])
        def api_download_key():
            return api_download_key_view()

        @app.route('/api/upload/', methods=['POST'])
        def api_upload():  # 一个分片上传后被调用
            return api_upload_view()

        @app.route('/api/upload/success', methods=['POST'])
        def api_upload_success():  # 所有分片均上传完后被调用
            return api_upload_success_view()

        @auth.login_required
        @app.route('/api/upload/token/', methods=['POST', 'GET'])
        def upload_token():
            return api_upload_token_view()

