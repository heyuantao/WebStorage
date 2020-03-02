#-*- coding=utf-8 -*-
import redis
from config import config
from utils import Singleton

@Singleton
class RedisClient:

    def init_app(self,app):
        connection_pool = redis.ConnectionPool(host='127.0.0.1',port=6370,db=0)
        redis_connection = redis.Redis(connection_pool=connection_pool)
        self.redis_connection = redis_connection
        print("This is redis reference info {} at init".format(self))

    def display(self):
        print("This is redis reference info {} at display".format(self))






