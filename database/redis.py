#-*- coding=utf-8 -*-
import redis
from config import config
from utils import Singleton

@Singleton
class RedisClient:
    def init_app(self, app=None):
        self.init_upload_token_information_database()
        self.init_upload_clip_information_database()

    def init_upload_token_information_database(self):
        connection_pool = redis.ConnectionPool(host='127.0.0.1', port=6370, db=0)
        redis_connection = redis.Redis(connection_pool=connection_pool)
        self.upload_token_redis_connection = redis_connection

    def init_upload_clip_information_database(self):
        connection_pool = redis.ConnectionPool(host='127.0.0.1', port=6370, db=1)
        redis_connection = redis.Redis(connection_pool=connection_pool)
        self.upload_clip_information_connection = redis_connection







