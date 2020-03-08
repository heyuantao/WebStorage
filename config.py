#-*- coding=utf-8 -*-
import os
from utils import Singleton
import logging

logger = logging.getLogger(__name__)

class FileStorageConfig:
    TMP_UPLOAD_PATH ="./data/tmp"                               #before merge
    UPLOAD_PATH = "./data/merged"                               #not end with slash


class AppConfig:
    SITE_URL = "http://127.0.0.1:5000"
    STATIC_FOLDER = "./templates/mystorageapp/build/static"  # not end with slash
    TEMPLATE_FOLDER = "./templates/mystorageapp/build"  # not end with slash
    AUTH_TOKEN = ["UseMyWebStorageService","6ea4ef99ab4a56e322c2bea276d6337c"]  #可以设置多个token
    CELERY_BACKEND = "redis://127.0.0.1:6379/1"

@Singleton
class Config:
    FileStorage = FileStorageConfig()
    App = AppConfig()

    def __init__(self):
        logger.critical("The auth token is {}".format(self.App.AUTH_TOKEN))

config = Config()
