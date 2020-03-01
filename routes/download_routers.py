#-*- coding=utf-8 -*-
from views.download_views import api_download_key_info_view,api_download_key_privateurl_view,api_download_key_view

def init_app(app):
    @app.route('/api/download/key/info', methods=['GET',])
    def api_download_key_info():
        return api_download_key_info_view()

    @app.route('/api/download/key/url/', methods=['GET',])
    def api_download_key_privateurl():
        return api_download_key_privateurl_view()

    @app.route('/api/download/key', methods=['GET',])
    def api_download_key():
        return api_download_key_view()