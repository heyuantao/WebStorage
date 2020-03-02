#-*- coding=utf-8 -*-
#from .redis import AppRedisClient
from utils import Singleton
from uuid import uuid4
from datetime import datetime,timedelta
import redis


@Singleton
class Database:
    def __init__(self, host='127.0.0.1', port=6370):
        self.token_prefix = "token"         #step one
        self.upload_prefix = "upload"       #step two
        self.merge_prefix = "merge"         #step three
        self.download_prefix = "download"
        self.host = host
        self.port = port

    def init_app(self,app=None):
        self.host='127.0.0.1'
        self.port=6370
        connection_pool = redis.ConnectionPool(self.host, self.port, db=0)
        self.connection = redis.Redis(connection_pool=connection_pool)
        print("KV database init finished !")

    def get_upload_task_by_key(self,key):
        connection = self.connection

        key_with_prefix = self.token_prefix+":"+key
        task = uuid4().hex

        if connection.exists(key_with_prefix):
            connection.expire(key_with_prefix, timedelta(hours=2))
            result = connection.get(key_with_prefix)
            return result
        connection.set(key_with_prefix, task)
        connection.expire(key_with_prefix, timedelta(hours =2))
        return task

    def append_clip_name_to_key(self, key, clip):
        connection = self.connection
        key_with_prefix = self.upload_prefix+":"+key
        connection.lpush(key_with_prefix, clip)

    def get_download_task_by_key(self, key):
        connection = self.connection

        key_with_prefix = self.download_prefix + ":" + key
        task = uuid4().hex

        if connection.exists(key_with_prefix):
            result = connection.get(key_with_prefix)
            return result
        connection.set(key_with_prefix,task)
        connection.expire(timedelta(hours =8))
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










