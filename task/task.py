#-*- coding=utf-8 -*-
#from __future__ import absolute_import

from celery import Celery
from celery.schedules import crontab
from config import config
from utils import Singleton,MessageException
from db import Database
from storage import Storage
import logging
import traceback

logger = logging.getLogger(__name__)
store = Storage()
db = Database()
celery = Celery("task", broker = config.App.CELERY_BACKEND)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(1.0, do_something.s('hello'), name='add every 10')

@celery.task
def do_something(msg):
    print("schedule task:{}".format(msg))
    logger.debug("schedule task:{}".format(msg))


@celery.task
def merge_file_by_key_in_celery(key):
    print("merge file begin in celery {}".format(key))
    store.merge_clip_of_key(key)
    db.clear_clip_upload_status_list_of_key(key)
    print("merge file end in celery {}".format(key))