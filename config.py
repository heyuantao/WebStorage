#-*- coding=utf-8 -*-
import os
from utils import Singleton

class FileStorageConfig:
    TMP_UPLOAD_PATH ="./data/tmp"                               #before merge
    UPLOAD_PATH = "./data/merged"                               #not end with slash


class AppConfig:
    SITE_URL = "http://127.0.0.1:5000"
    STATIC_FOLDER = "./templates/mystorageapp/build/static"  # not end with slash
    TEMPLATE_FOLDER = "./templates/mystorageapp/build"  # not end with slash
    AUTH_TOKEN = ["1234567890","abcdefghi"]
    CELERY_BACKEND = "redis://127.0.0.1:6379/1"

@Singleton
class Config:
    FileStorage = FileStorageConfig()
    App = AppConfig()

config = Config()