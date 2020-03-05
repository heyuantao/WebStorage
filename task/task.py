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
    #hour =60*60*60
    hour = 60*1
    sender.add_periodic_task(hour, clear_upload_failure_clips.s(), name='add every 10')

@celery.task
def do_something(msg):
    print("schedule task:{}".format(msg))
    logger.debug("schedule task:{}".format(msg))

#大文件可能需要较长的合并时间，因此将合并文件的任务在后台进行
@celery.task
def merge_file_by_key_in_celery(key):
    print("merge file begin in celery {}".format(key))
    store.merge_clip_of_key(key)
    db.clear_clip_upload_status_list_of_key(key)
    print("merge file end in celery {}".format(key))

#上传文件的过程中可能存在上传失败的任务，这些任务会留下部分上传成功的文件分片，因此将这些分片进行清理,该任务被周期调用
@celery.task
def clear_upload_failure_clips():
    print("delete clip task begin")
    upload_failure_key_list = db.get_upload_failure_key_list()
    print("failure updload key list:{}".format(upload_failure_key_list))
    for upload_failure_key_item in upload_failure_key_list:
        #此时获得的都是一些上传失败的任务，因此clip_list 不包含'success'的标记
        clip_list = db.get_clip_upload_status_list_of_key(upload_failure_key_item)
        for clip_item in clip_list:
            print("delete clip {}".format(clip_item))
            store.delete_clip(clip_item)

        db.clear_clip_upload_status_list_of_key(upload_failure_key_item)
    print("delete clip task end ")