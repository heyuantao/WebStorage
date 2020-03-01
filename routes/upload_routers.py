#-*- coding=utf-8 -*-
from views.upload_views import api_upload_view, api_upload_success_view, api_upload_token_view
from auth import get_auth
def init_app(app):


    @app.route('/api/upload/', methods=['POST'])
    def api_upload():  # 一个分片上传后被调用
        return api_upload_view()


    @app.route('/api/upload/success', methods=['POST'])
    def api_upload_success():  # 所有分片均上传完后被调用
        return api_upload_success_view()


    @app.route('/api/upload/token/', methods=['POST', 'GET'])
    def upload_token():
        return api_upload_token_view()
