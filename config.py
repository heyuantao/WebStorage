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
    AUTH_TOKEN = ["UseMyWebStorageService","6ea4ef99ab4a56e322c2bea276d6337c"]  #可以设置多个token,可以设置并修改
    CELERY_BACKEND = "redis://127.0.0.1:6379/1"

@Singleton
class Config:
    FileStorage = FileStorageConfig()
    App = AppConfig()

    def __init__(self):
        default_token_list = ["UseMyWebStorageService","6ea4ef99ab4a56e322c2bea276d6337c"]
        for token_item in default_token_list:
            if token_item in self.App.AUTH_TOKEN:
                logger.critical("The default auth token \"{}\" is using .This may cause secure problem !".format(token_item))


config = Config()
