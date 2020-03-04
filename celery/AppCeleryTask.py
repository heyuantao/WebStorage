#-*- coding=utf-8 -*-
#from .redis import AppRedisClient
from utils import Singleton,MessageException
import redis
import logging
import traceback

logger = logging.getLogger(__name__)

class AppCeleryTask:
    pass