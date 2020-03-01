#-*- coding=utf-8 -*-
import os

class Storage:
    #tmp_path is directory for file clip,file path is the directory for file merged and serve
    def __init(self,tmp_path,file_path):
        self.tmp_path = tmp_path
        self.file_path = file_path
        if os.path.isabs(self.tmp_path)



