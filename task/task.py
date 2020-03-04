#-*- coding=utf-8 -*-
from __future__ import absolute_import
from utils import Singleton,MessageException
from celery import Celery
from config import config
from db import Database
from storage import Storage
import redis
import logging
import traceback

store = Storage()
db = Database()

celery = Celery("task", broker = config.App.CELERY_BACKEND)

@celery.task
def do_something():
    print(db.get_file_list_cache())

@celery.task
def merge_file_by_key_in_celery(key):
    print("merge file begin in celery {}".format(key))
    store.merge_clip_of_key(key)
    print("merge file end in celery {}".format(key))