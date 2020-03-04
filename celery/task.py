#-*- coding=utf-8 -*-
#from .redis import AppRedisClient
from utils import Singleton,MessageException
from celery import Celery
from config import config
import redis
import logging
import traceback

logger = logging.getLogger(__name__)

@Singleton
class AsyncTask:
    def __init__(self,backend=config.App.CELERY_BACKEND):
        self.backend = backend

    def init_app(self,app=None):
        logger.debug("Init task app in AsyncTask")
        celery = Celery(app.name, broker = self.backend)
        self.celery = celery

        @celery.task
        def calc(arg1,arg2):
            return arg1+arg2