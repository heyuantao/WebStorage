#-*- coding=utf-8 -*-
#from .redis import AppRedisClient
from utils import Singleton,MessageException
from uuid import uuid4
from datetime import datetime,timedelta
from config import config
import redis
import logging
import traceback
from storage import Storage

logger = logging.getLogger(__name__)

#标识可下载文件列表的状态
class DownloadFileStatus:
    PRESENT="present"       #文件在磁盘存放
    DELETING="deleting"     #文件待删除

#使用redis来存放各类数据
@Singleton
class Database:
    def __init__(self, host='127.0.0.1', port=6370 , db=0):
        self.host = host
        self.port = port
        self.db = db
        #各个状态列队在内存中的标识，用prefix:key的方式来表示
        self.file_prefix        = "file:"         #浏览阶段，软件初始化时将文件内容信息从目录中读入redis缓存，并根据缓存在判断文件是否存在
        self.task_prefix        = "task:"         #上传前期，根据上传对项目key来生成对应的上传编号
        self.upload_prefix      = "upload:"       #分片上传节点，用列表方式记录了每个分片信息，列表最后用success来表示分片是否上传完成
        self.merge_prefix       = "merge:"        #合并节点
        self.download_prefix    = "download:"     #下载阶段


    #flask 初始化调用该函数
    def init_app(self,app=None):
        try:
            logger.debug("Connect to redis ...")
            self.connection_pool = redis.ConnectionPool(host=self.host, port=self.port, db=0, decode_responses=True) #password
            self.connection = redis.StrictRedis(connection_pool=self.connection_pool)
        except Exception as e:
            logger.error("Error in conncetion redis !")
            raise MessageException('Error in conncetion redis at Database.init_app() ')


    #---------------------------上传前期处理函数--------------------------------------#
    #通过文件名key来获得对应的task编号，如果对应的key存在，则直接返回，否则在redis数据库中创建task编号并返回
    def get_upload_task_by_key(self,key):
        connection = self.connection

        key_with_prefix = self.task_prefix+key
        task = str(uuid4().hex)

        if connection.exists(key_with_prefix):
            connection.expire(key_with_prefix, timedelta(hours=2))
            result = connection.get(key_with_prefix)
            return result
        connection.set(key_with_prefix, task)
        connection.expire(key_with_prefix, timedelta(hours =2))
        return task

    #检查文件名key和task编号是否匹配，该函数被上传函数调用，用于检查上传是否合法
    def is_upload_task_valid(self,key,task):
        connection = self.connection

        key_with_prefix = self.task_prefix + key
        if connection.exists(key_with_prefix):
            result = connection.get(key_with_prefix)
            if result == task:
                return True
            else:
                return False
        else:
            return False

    #清除文件名key对应的task编号，在文件所有分片上传完成后被调用
    def _delete_upload_task_by_key(self,key):
        connection = self.connection
        key_with_prefix = self.task_prefix + key
        connection.delete(key_with_prefix)
    #--------------------------------------------------------------------------------#

    #------------------------------分片处理函数---------------------------------------#
    #将上传的文件分片信息记录到redis中，该记录以list进行保存，list的每个内容为分片的文件名，在上传彻底结束后，该list还有有一个"success"的内容
    def append_clip_upload_partial_status_of_key(self, key, clip_name):
        key_with_prefix = self.upload_prefix + key
        self.connection.lpush(key_with_prefix, clip_name)

    #分片上传完成后，将成功的信息记录在key对应的分片列表中，该函数在文件分片全部上传完成后被调用
    def append_clip_upload_success_status_of_key(self, key):
        key_with_prefix = self.upload_prefix + key
        self.connection.lpush(key_with_prefix,"success")

        self._delete_upload_task_by_key(key)

    #清除key对应的分片列表的内容，该函数在分片文件合并完成后被调用
    def clear_clip_upload_status_list_of_key(self, key):
        key_with_prefix = self.upload_prefix + key
        self.connection.delete(key_with_prefix)

    def get_clip_upload_status_list_length_of_key(self, key):
        key_with_prefix = self.upload_prefix + key
        return self.connection.llen(key_with_prefix)-1          #success is not count
    #--------------------------------------------------------------------------------#

    #-------------------------------------文件下载处理函数-----------------------------#
    #根据传入的文件名key，生成下载任务的task，并根据key和task来生成下载链接
    def get_download_task_by_key(self, key):
        connection = self.connection
        key_with_prefix = self.download_prefix + key
        task = str(uuid4().hex)

        if connection.exists(key_with_prefix):
            result = connection.get(key_with_prefix)
            return result

        connection.set(key_with_prefix,task)
        connection.expire(key_with_prefix,timedelta(hours =1))
        return task

    #检验下载链接的key和task是否有效
    def is_download_task_valid(self,key,task):
        connection = self.connection

        key_with_prefix = self.download_prefix + key
        if connection.exists(key_with_prefix):
            result = connection.get(key_with_prefix)
            if result == task:
                return True
            else:
                return False
        else:
            return False
    #---------------------------------------------------------------------------------#

    # -------------------------------------文件列表函数--------------------------------#
    #当文件合并完成，将文件加入文件列表中
    def add_to_downloadable_file_list_by_key(self, key):
        key_with_prefix = self.file_prefix + key
        self.connection.set(key_with_prefix,DownloadFileStatus.PRESENT)

    #从缓存中删除某个文件
    def delete_downloadable_file_list_by_key(self, key):
        key_with_prefix = self.file_prefix + key
        self.connection.delete(key_with_prefix)
        #self.connection.set(key_with_prefix, DownloadFileStatus.PRESENT)

    #返回缓存的文件列表
    def get_file_list_cache(self):
        file_pattern = self.file_prefix + "*"
        matched_file_name_with_prefix_list = self.connection.keys(pattern=file_pattern)
        matched_file_name_without_prefix_lit = []
        begin = len(self.file_prefix)
        for item_with_prefix in matched_file_name_with_prefix_list:
            if item_with_prefix.startswith(self.file_prefix):
                file_name_without_prefix = item_with_prefix[begin:]
                matched_file_name_without_prefix_lit.append(file_name_without_prefix)
        return matched_file_name_without_prefix_lit
    # ---------------------------------------------------------------------------------#





