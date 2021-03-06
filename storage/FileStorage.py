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

                    if logger.getEffectiveLevel() == logging.DEBUG:
                        logger.critical("The app is in debug mode, the merge process will execute slowly !")
                        time.sleep(5)

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
        try:
            file_abs_path = os.path.join(self.file_path, key)
            if os.path.exists(file_abs_path):
                os.remove(file_abs_path)
            else:
                logger.error("Delete a file \"{}\" which is not exist ! in FileStorage.delete_by_key() ".format(key))
        except Exception as e:
            logger.critical("Delete a file \"{}\" error ! in FileStorage.delete_by_key() ".format(key))

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

    def get_content_size_of_key(self,key):
        file_abs_path = os.path.join(self.file_path, key)
        return os.stat(str(file_abs_path)).st_size

    def get_merging_content_size_of_key(self, key, clip_list):

        clip_list_len = len(clip_list)-1        #不计算'success' 这个标记
        if "success" not in clip_list:
            msg_str = "You are download a key:\"{}\" which is not merge successfull in FileStorage.get_merging_content_size_of_key()".format(key)
            logger.critical(msg_str)
            raise  MessageException(msg_str)
        last_chunk_count = clip_list_len-1      #最后一个分片的名字
        number_of_5m_chunk = clip_list_len-1    #5M分片的数量，只有最后一个分片大小不为5M
        last_clip_abs_path = "{0}/{1}{2}".format(self.tmp_path, key, last_chunk_count)

        #根据分片计算文件大小
        clip_total_size = number_of_5m_chunk*5*1024*1024
        clip_total_size = clip_total_size + os.stat(str(last_clip_abs_path)).st_size
        '''
        for item_clip in clip_list:
            if item_clip=='success':
                continue
            try:
                clip_abs_path = os.path.join(self.tmp_path, item_clip)
                clip_total_size = clip_total_size + os.stat(str(clip_abs_path)).st_size
            except IOError:
                continue
        '''
        return clip_total_size


    #用于处理部分请求时的函数，此时key已经合并完成
    def get_partial_content_generate_of_key(self, key, begin, length):
        file_abs_path = os.path.join(self.file_path, key)
        chunk_size = 5 * 1024 * 1024
        file = open(file_abs_path, 'rb')
        current = begin
        end = begin + length
        while True:
            if (end-current) > chunk_size:
                size_to_read = chunk_size
                file.seek(current)
                data = file.read(size_to_read)
                current = current + size_to_read
                yield data
                continue
            elif 0<(end-current)<chunk_size:
                size_to_read = end-current
                file.seek(current)
                data = file.read(size_to_read)
                current = current + size_to_read
                yield data
                continue
            else:
                break

        file.close()

    # 用于处理部分请求时的函数，此时key仍在合并状态
    def get_partial_merging_content_generate_of_key_and_clipinforamtion(self, key, clip_list, begin, length):
        clip_count = len(clip_list)-1
        #begin, end = 0, clip_count-1    #分片的开始标记和结束标记，类似key{begin}和key{end}
        chunk_size = 5*1024*1024
        #chunk = 0                        #chunk为文件分片序号，从0到clip_count-1
        #current = begin
        end = begin+length

        first_chunk = int(begin / chunk_size)
        first_chunk_seek = begin % chunk_size
        first_chunk_size_to_read = chunk_size - first_chunk_seek  #必须考虑first 和 last chunk 在一个分片中的情况，修改代码

        last_chunk = int(end / chunk_size)
        last_chunk_seek = 0
        last_chunk_size_to_read = end % chunk_size

        #如果要读的内容都在一个分片之中，则要修正第一个分片读的长度，即不能读到5M结束的位置
        if first_chunk==last_chunk:
            first_chunk_size_to_read = length

        #先从分片开始读，如果出现错误，再从合并过的文件开始读
        try:
            for current_chunk in range(first_chunk, last_chunk+1):
                clip_file_name = "{0}/{1}{2}".format(self.tmp_path, key, current_chunk)
                if current_chunk == first_chunk:
                    clip_file = open(clip_file_name, "rb")
                    clip_file.seek(first_chunk_seek)
                    clip_file_content = clip_file.read(first_chunk_size_to_read)
                    yield clip_file_content
                    clip_file.close()
                    continue
                elif current_chunk == last_chunk:
                    clip_file = open(clip_file_name, "rb")
                    clip_file.seek(last_chunk_seek)
                    clip_file_content = clip_file.read(last_chunk_size_to_read)
                    yield clip_file_content
                    clip_file.close()
                    continue
                else:
                    clip_file = open(clip_file_name, "rb")
                    clip_file_content = clip_file.read()
                    yield clip_file_content
                    clip_file.close()
                    continue
        except IOError:
            logger.error("This clip \"{}\" not exist in Storage.get_partial_merging_content_generate_of_key_and_clipinforamtion()".format(clip_file_name))
        #先判断是在读取分片的时候是否已经读取完毕，如果完毕则下面的程序不执行
        if current_chunk == last_chunk:
            return

        #当执行到此步骤时，说明合并过程导致分片被删除，因此后续需要从合并过的文件中来读
        error_at_this_chunk = current_chunk
        try:
            merged_file_path = os.path.join(self.file_path, key)
            merged_file = open(merged_file_path, "rb")
            for current_chunk in range(error_at_this_chunk, last_chunk+1):
                if current_chunk == first_chunk:
                    merged_file.seek(first_chunk_seek)
                    chunk_content = merged_file.read(first_chunk_size_to_read)
                    yield chunk_content
                    continue
                elif current_chunk == last_chunk:
                    merged_file.seek(last_chunk_seek)
                    chunk_content = merged_file.read(last_chunk_size_to_read)
                    yield chunk_content
                    continue
                else:
                    merged_file.seek(current_chunk*chunk_size)
                    chunk_content = merged_file.read(chunk_size)
                    yield chunk_content
                    continue
            merged_file.close()
        except IOError:
            logger.critical("Read merged file \"{}\" error, this may be a bug in Storage.get_partial_merging_content_generate_of_key_and_clipinforamtion()".format(merged_file_path))
