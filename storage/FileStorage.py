#-*- coding=utf-8 -*-
from utils import MessageException
from utils import Singleton
from config import config
import os
import time
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

    #删除文件的分片，clip_name是分片的名字
    def delete_clip(self,clip_name):
        clip_abs_path = os.path.join(self.tmp_path,clip_name)
        try:
            os.remove(clip_abs_path)
        except IOError:
            logger.error("Delete clip \"{}\" error in FileStorage.delete_clip()".format(clip_abs_path))

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
        clip_file_list = []
        with open(saved_file_path, 'wb') as saved_file:  # 创建新文件
            while True:
                try:
                    #filename = self.tmp_path + '/%s%d' % (key, chunk)
                    clip_file_name = "{0}/{1}{2}".format(self.tmp_path, key, chunk)
                    #time.sleep(3)
                    clip_file = open(clip_file_name, 'rb')                              # 按序打开每个分片
                    saved_file.write(clip_file.read())
                    clip_file.close()
                except IOError:
                    break
                chunk += 1
                clip_file_list.append(clip_file_name)
                #os.remove(clip_file_name) # 删除该分片，节约空间
        #待所有文件合并后，删除分片，这样确保总有可用的文件分片在磁盘上存储
        for item in clip_file_list:
            os.remove(item)


    #从磁盘中删除文件
    def delete_by_key(self, key):
        file_abs_path = os.path.join(self.file_path, key)
        if os.path.exists(file_abs_path):
            os.remove(file_abs_path)
        else:
            logger.info("Delete a file \"{}\" with is not exist on disk !".format(key))

    #处理文件的读，采用yield的方式来读取，防止一次占用过多的内存,在此处应当处理几种情况，1.文件合并已经完成（直接读） 2.文件正在合并
    def get_content_generate_of_key(self, key):    #可能会抛出异常
        file_abs_path = os.path.join(self.file_path,key)
        chunk_size = 5*1024*1024
        file = open(file_abs_path,'rb')

        while True:
            data = file.read(chunk_size)
            if not data:
                break
            yield data

        file.close()


    #clip_list 包含了"success"状态，合并文件的过程会先产生合并后的文件，该文件生成后再去删除各个文件分片
    def get_merging_content_generate_of_key_and_clipinforamtion(self, key, clip_list):
        clip_count = len(clip_list)-1
        begin, end = 0, clip_count-1    #分片的开始标记和结束标记，类似key{begin}和key{end}
        chunk_size = 5*1024*1024
        chunk = 0                        #chunk为文件分片序号，从0到clip_count-1
        #for chunk in range(clip_count):
        while True:
            # 分片已经结束
            if chunk>end:
                break
            #分片没有结束
            clip_file_name = "{0}/{1}{2}".format(self.tmp_path, key, chunk)
            #首先读文件分片，如果出错再去读合并后的文件
            try:
                clip_file = open(clip_file_name,"rb")
                clip_file_content = clip_file.read()
                yield clip_file_content
                clip_file.close()
                chunk = chunk+1
                continue
            except IOError:
                logger.debug("This clip \"{}\" not exist".format(clip_file_name))


            #合并后的文件
            merged_file_path = os.path.join(self.file_path, key)
            try:
                seek_postion =chunk_size*chunk
                merged_file = open(merged_file_path,"rb")
                merged_file.seek(seek_postion)
                content = merged_file.read(chunk_size)
                merged_file.close()
                yield content
                chunk = chunk+1
                continue
            except IOError:
                logger.error("Read Merged file \"{}\" should not be error, this may be a bug !".format(merged_file_path))

