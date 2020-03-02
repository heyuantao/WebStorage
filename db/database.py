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
        self.host = host
        self.port = port

    def init_app(self,app=None):
        self.host='127.0.0.1'
        self.port=6370
        connection_pool = redis.ConnectionPool(self.host, self.port, db=0)
        self.connection = redis.Redis(connection_pool=connection_pool)

    def get_upload_task_by_key(self,key):
        connection = self.connection

        task = uuid4().hex
        key_with_prefix = self.token_prefix+":"+key
        value_dict = {'key':key, 'task':task}

        if connection.exists(key_with_prefix):
            result = connection.hgetall(key_with_prefix)
            connection.expire(timedelta(hours=2))
            return result
        connection.hmset(key_with_prefix,value_dict)
        connection.expire(timedelta(hours =2))
        return value_dict

    def append_clip_name_to_key(self, key, clip):
        connection = self.connection
        key_with_prefix = self.upload_prefix+":"+key


        pass







