#-*- coding=utf-8 -*-
from utils import MessageException
from utils import Singleton
from config import config
import os
import logging

logger = logging.getLogger(__name__)

APP_PATH = os.getcwd()
TMP_UPLOAD_PATH = os.path.join(APP_PATH, config.FileStorage.TMP_UPLOAD_PATH)
UPLOAD_PATH = os.path.join(APP_PATH, config.FileStorage.UPLOAD_PATH)

@Singleton
class FileStorage:
    #tmp_path is directory for file clip,file path is the directory for file merged and serve
    def __init__(self, tmp_path=TMP_UPLOAD_PATH, file_path=UPLOAD_PATH):
        self.tmp_path = tmp_path
        self.file_path = file_path
        if not os.path.isabs(self.tmp_path):
            raise MessageException('tmp_path :{} is not absolute dir in Storage.__init__()'.format(self.tmp_path))
        if not os.path.isabs(self.file_path):
            raise MessageException('file_path :{} is not absolute dir in Storage.__init__()'.format(self.file_path))

    def init_app(self,app=None):
        logger.debug("Use FileStorage the temp_path and file_path is {} {}".format(self.tmp_path,self.file_path))

    def keyInfo(self,key):
        file_path = os.path.join(self.file_path,key)
        if not os.path.exists(file_path):
            raise MessageException('file {} not exist'.format(file_path))
        key_info_dict = {'key':key,'file_path':file_path}
        return key_info_dict

    def getUploadFileList(self):
        uploaded_dir_path = self.file_path
        file_list = []
        #print(uploaded_dir_path)
        for item in os.listdir(uploaded_dir_path):
            item_abs_path = os.path.join(uploaded_dir_path,item)
            if os.path.isfile(item_abs_path):
                file_list.append(item)
        #print(file_list)
        return file_list

