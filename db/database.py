#-*- coding=utf-8 -*-
#from .redis import AppRedisClient
from utils import Singleton,MessageException
from uuid import uuid4
from datetime import datetime,timedelta
import redis
import logging
import traceback
from storage import Storage

logger = logging.getLogger(__name__)

@Singleton
class Database:
    def __init__(self, host='127.0.0.1', port=6370):
        self.file_prefix = "file"
        self.token_prefix = "token"         #step one
        self.upload_prefix = "upload"       #step two
        self.merge_prefix = "merge"         #step three
        self.download_prefix = "download"
        self.host = host
        self.port = port

    def init_app(self,app=None):
        self.host='127.0.0.1'
        self.port=6379

        try:
            logger.debug("Connect to redis ...")
            self.connection_pool = redis.ConnectionPool(host=self.host, port=self.port, db=0, decode_responses=True) #password
            self.connection = redis.StrictRedis(connection_pool=self.connection_pool)
        except Exception as e:
            logger.error("Error in conncetion redis !")
            raise MessageException('Error in conncetion redis at Database.init_app() ')


        try:
            pattern = self.file_prefix+":*"
            self.connection.delete(*self.connection.keys(pattern=pattern))      #clear the old data

            logger.debug("Read upload file list to redis ...")
            storage = Storage()
            upload_file_list = storage.getUploadFileList()
            for key in upload_file_list:
                key_with_prefix = self.file_prefix + ":" + key
                self.connection.set(key_with_prefix,"")
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error("Error in read upload file list to redis !")
            raise MessageException('Error in read upload file list to redis at Database.init_app() ')



    def get_upload_task_by_key(self,key):
        connection = self.connection

        key_with_prefix = self.token_prefix+":"+key
        task = str(uuid4().hex)

        if connection.exists(key_with_prefix):
            connection.expire(key_with_prefix, timedelta(hours=2))
            result = connection.get(key_with_prefix)
            return result
        connection.set(key_with_prefix, task)
        connection.expire(key_with_prefix, timedelta(hours =2))
        return task

    def is_upload_task_valid(self,key,task):
        connection = self.connection

        key_with_prefix = self.token_prefix + ":" + key
        if connection.exists(key_with_prefix):
            result = connection.get(key_with_prefix)
            if result == task:
                return True
            else:
                return False
        else:
            return False

    def clear_upload_task_by_key(self,key):
        connection = self.connection
        key_with_prefix = self.token_prefix + ":" + key
        connection.delete(key_with_prefix)

    def append_clip_name_to_key(self, key, clip_name):
        connection = self.connection
        key_with_prefix = self.upload_prefix+":"+key
        connection.lpush(key_with_prefix, clip_name)

    def clear_clip_list_by_key(self, key):
        connection = self.connection
        key_with_prefix = self.upload_prefix + ":" + key
        connection.delete(key_with_prefix)

    def get_download_task_by_key(self, key):
        connection = self.connection
        key_with_prefix = self.download_prefix + ":" + key
        task = str(uuid4().hex)

        if connection.exists(key_with_prefix):
            result = connection.get(key_with_prefix)
            return result
        connection.set(key_with_prefix,task)
        connection.expire(key_with_prefix,timedelta(hours =8))
        return task

    def is_download_task_valid(self,key,task):
        connection = self.connection

        key_with_prefix = self.download_prefix + ":" + key
        if connection.exists(key_with_prefix):
            result = connection.get(key_with_prefix)
            if result == task:
                return True
            else:
                return False
        else:
            return False










