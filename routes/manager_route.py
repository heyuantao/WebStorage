#-*- coding=utf-8 -*-
from flask import render_template, request, session, jsonify
from views.download_views import api_file_info_view, api_file_url_view, file_content_view, \
    file_freecontent_view
from views.file_views import api_file_list_view, api_file_delete_view
from views.upload_views import api_upload_view, api_upload_success_view, api_upload_token_view, api_upload_info_view
from config import config

ROUTER_PREFIX = config.App.ROUTE_PREFIX

class Route:

    def init_app(self, app=None, auth=None):
        @app.route(ROUTER_PREFIX+'/api/', methods=['GET', ])
        def index():
            return render_template('index.html')


        #------------------------------------用于文件下载的管理接口---------------------------------#
        '''
        @app.route('/api/download/content', methods=['GET',])  #下载文件
        def api_download_key():
            return api_download_view()

        @app.route('/api/download/freecontent', methods=['GET',])  #下载文件
        def api_free_download_key():
            return api_free_download_view()
        '''
        # ------------------------------------------------------------------------------------#

        # ------------------------------------用于文件上传的接口---------------------------------#
        @app.route(ROUTER_PREFIX+'/api/upload/', methods=['POST'])
        def api_upload():  # 一个分片上传后被调用
            return api_upload_view()

        @app.route(ROUTER_PREFIX+'/api/upload/success/', methods=['POST'])
        def api_upload_success():  # 所有分片均上传完后被调用
            return api_upload_success_view()


        @app.route(ROUTER_PREFIX+'/api/upload/token/', methods=['POST'])
        @auth.login_required
        def upload_token():
            return api_upload_token_view()

        @app.route(ROUTER_PREFIX+'/api/upload/info/', methods=['POST'])       #获取上传task的信息，主要是获取size的大小，即上传文件大小的限制
        #@auth.login_required                                   #该接口用于给javascript客户端验证文件大小
        def upload_info():
            return api_upload_info_view()
        # ------------------------------------用于文件上传的接口---------------------------------#

        # ------------------------------------用于文件管理的接口---------------------------------#
        @app.route(ROUTER_PREFIX+'/api/file/list/', methods=['POST'])
        @auth.login_required
        def api_file_list():            # 查看当前的文件列表
            return api_file_list_view()

        @app.route(ROUTER_PREFIX+'/api/file/delete/', methods=['POST'])
        @auth.login_required
        def api_file_delete():            # 删除文件，key为文件名
            return api_file_delete_view()

        @app.route(ROUTER_PREFIX+'/api/file/info/', methods=['POST'])     #获取文件信息，可以查看文件是否存在
        @auth.login_required
        def api_file_info():
            return api_file_info_view()

        @app.route(ROUTER_PREFIX+'/api/file/url/', methods=['POST'])     #获取文件的下载链接
        @auth.login_required
        def api_file_url():
            return api_file_url_view()
        # ------------------------------------用于文件管理的接口---------------------------------#

