#-*- coding=utf-8 -*-
import os
from exceptions import MessageException

class Storage:
    #tmp_path is directory for file clip,file path is the directory for file merged and serve
    def __init(self,tmp_path,file_path):
        self.tmp_path = tmp_path
        self.file_path = file_path
        if not os.path.isabs(self.tmp_path):
            raise MessageException('tmp_path :{} is not absolute dir in Storage.__init__()'.format(self.tmp_path))
        if not os.path.isabs(self.file_path):
            raise MessageException('file_path :{} is not absolute dir in Storage.__init__()'.format(self.file_path))

    def keyInfo(self,key):
        file_path = os.path.join(self.file_path,key)
        if not os.path.exists(file_path):
            raise MessageException('file {} not exist'.format(file_path))
        key_info_dict = {'key':key,'file_path':file_path}
        return key_info_dict

