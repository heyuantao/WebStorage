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
    hour = 60*20
    little_time = 60*2
    sender.add_periodic_task(little_time, clear_upload_failure_clips.s(), name="clear_upload_failure_clip")
    sender.add_periodic_task(little_time, delete_file_marked_as_deleting.s(), name="delete_file_mark_as_deleting")


#大文件可能需要较长的合并时间，因此将合并文件的任务在后台进行
@celery.task
def merge_file_by_key_in_celery(key):
    #print("merge file begin in celery {}".format(key))
    logger.info("Merge \"{}\" in task.merge_file_by_key_in_celery()".format(key))
    store.merge_clip_of_key(key)
    db.clear_clip_upload_status_list_of_key(key)
    logger.info("Merge \"{}\" finished in task.merge_file_by_key_in_celery() ".format(key))

#上传文件的过程中可能存在上传失败的任务，这些任务会留下部分上传成功的文件分片，因此将这些分片进行清理,该任务被周期调用
@celery.task
def clear_upload_failure_clips():
    upload_failure_key_list = db.get_upload_failure_key_list()
    logger.info("Find upload failure key list:{} in task.clear_upload_failure_clips() ".format(upload_failure_key_list))
    for upload_failure_key_item in upload_failure_key_list:
        #此时获得的都是一些上传失败的任务，因此clip_list 不包含'success'的标记
        clip_list = db.get_clip_upload_status_list_of_key(upload_failure_key_item)
        for clip_item in clip_list:
            logger.info("Delete upload failure key \"{}\" clip \"{}\" in task.clear_upload_failure_clips() ".format(upload_failure_key_item, clip_item))
            store.delete_clip(clip_item)

        db.clear_clip_upload_status_list_of_key(upload_failure_key_item)
        logger.info("Delete upload failure key \"{}\" finished in task.clear_upload_failure_clips() ".format(upload_failure_key_item))
    #print("delete clip task end ")


#清除标记为待删除的文件，由于文件可能处于合并状态，对于此类文件等待下次执行时再删除
@celery.task
def delete_file_marked_as_deleting():
    deleting_file_list = db.get_deleting_file_list()
    for deleting_file_item in deleting_file_list:
        if db.is_key_contents_in_merge_status(deleting_file_item):
            logger.error("Key \"{}\" is in merge status ,delete it next time in task.clear_key_marked_as_deleting() ".format(deleting_file_item))
            continue
        try:
            store.delete_by_key(deleting_file_item)
            db.delete_file_from_deleting_file_list_by_key(deleting_file_item)
        except Exception as e:
            logger.critical("Error Happend when delete \"{}\" in db and store in task.delete_file_marked_as_deleting() ".format(deleting_file_item))

