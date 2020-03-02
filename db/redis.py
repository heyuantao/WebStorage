#-*- coding=utf-8 -*-
import redis
from config import config

class AppRedisClient:
    def __init__(self,host='127.0.0.1',port=6370):
        self.host = host
        self.port = port
        self.init_task_database()
        self.init_clip_database()

    def init_task_database(self):
        connection_pool = redis.ConnectionPool(self.host, self.port, db=0)
        redis_connection = redis.Redis(connection_pool=connection_pool)
        self.task_database_connection = redis_connection

    def init_clip_database(self):
        connection_pool = redis.ConnectionPool(self.host, self.port, db=1)
        redis_connection = redis.Redis(connection_pool=connection_pool)
        self.clip_database_connection = redis_connection









