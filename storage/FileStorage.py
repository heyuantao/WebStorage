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

    def get_upload_file_list(self):
        uploaded_dir_path = self.file_path
        file_list = []
        for item in os.listdir(uploaded_dir_path):
            item_abs_path = os.path.join(uploaded_dir_path,item)
            if os.path.isfile(item_abs_path):
                file_list.append(item)
        return file_list

    #将上传的文件分片进行保存，file为文件分片，chunk为分片的编号
    def save_clip(self,clip, key, chunk):
        clip_filename = '%s%s' % (key, chunk)               # 构成该分片唯一标识符
        clip.save(self.tmp_path + '/%s' % clip_filename)  # 保存分片到本地

    #合并文件
    def merge_clip_of_key(self,key):
        chunk = 0
        saved_file_name = key
        saved_file_path = "{0}/{1}".format(self.file_path, saved_file_name)

        #with open(self.file_path + '/%s' % (saved_filename), 'wb') as target_file:  # 创建新文件
        with open(saved_file_path, 'wb') as saved_file:  # 创建新文件
            while True:
                try:
                    #filename = self.tmp_path + '/%s%d' % (key, chunk)
                    clip_file_name = "{0}/{1}{2}".format(self.tmp_path, key, chunk)
                    clip_file = open(clip_file_name, 'rb')                              # 按序打开每个分片
                    saved_file.write(clip_file.read())
                    clip_file.close()
                except IOError:
                    break
                chunk += 1
                os.remove(clip_file_name)                                                    # 删除该分片，节约空间
