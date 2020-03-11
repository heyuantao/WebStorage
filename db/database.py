#-*- coding=utf-8 -*-
#from .redis import AppRedisClient
from utils import Singleton,MessageException
from uuid import uuid4
from datetime import datetime,timedelta
from config import config
import redis
import logging
import json
import traceback
from storage import Storage

logger = logging.getLogger(__name__)

#标识可下载文件列表的状态
class DownloadFileStatus:
    PRESENT="present"       #文件在磁盘存放
    DELETING="deleting"     #文件待删除


#使用redis来存放各类数据
@Singleton
class Database:
    def __init__(self, host='127.0.0.1', port=6379 , db=0):
        self.host = host
        self.port = port
        self.db = db
        #各个状态列队在内存中的标识，用prefix:key的方式来表示
        #self.file_prefix        = "file:"         #浏览阶段，软件初始化时将文件内容信息从目录中读入redis缓存，并根据缓存在判断文件是否存在
        self.task_prefix        = "task:"         #上传前期，根据上传对项目key来生成对应的上传编号
        self.upload_prefix      = "upload:"       #分片上传节点，用列表方式记录了每个分片信息，列表最后用success来表示分片是否上传完成
        self.merge_prefix       = "merge:"        #合并节点
        self.download_prefix    = "download:"     #下载阶段

        self.file_list_key          = "file_list"           #文件的哈希列表，用于下载和浏览，以(filename,status)的方式进行存放
        self.file_deleting_list_key = "file_deleting_list"  #待删除文件的哈希列表，待后端异步任务进行删除

        try:
            logger.debug("Connect to redis ... in Database.__init__()")
            self.connection_pool = redis.ConnectionPool(host=self.host, port=self.port, db=self.db, decode_responses=True) #password
            self.connection = redis.StrictRedis(connection_pool=self.connection_pool)
        except Exception as e:
            msg_str = "Error in conncetion redis ! in Database.__init__()"
            logger.error(msg_str)
            raise MessageException(msg_str)

    #flask 初始化调用该函数
    def init_app(self,app=None):
        logger.debug("Init database in Database.__init__()")

    #---------------------------上传前期处理函数--------------------------------------#
    #先查看该key是否被占用，因为key可能已经在文件列表或者在删除列表中
    def is_key_occupied(self,key):
        if self.connection.hexists(self.file_list_key,key):
            return True
        if self.connection.hexists(self.file_deleting_list_key,key):
            return True
        return False

    #通过文件名key来获得对应的task编号，如果对应的key存在，则直接返回，否则在redis数据库中创建task编号并返回
    def get_upload_task_by_key(self,key):
        key_with_prefix = self.task_prefix+key
        #检查是否已经存在
        if self.connection.exists(key_with_prefix):
            self.connection.expire(key_with_prefix, timedelta(hours=2))
            result = self.connection.get(key_with_prefix)
            return result
        #不存在则生成新的task编号
        task = str(uuid4().hex)
        self.connection.set(key_with_prefix, task)
        self.connection.expire(key_with_prefix, timedelta(hours =2))
        return task

    #检查文件名key和task编号是否匹配，该函数被上传函数调用，用于检查上传是否合法
    def is_upload_task_valid(self,key,task):
        key_with_prefix = self.task_prefix + key
        if self.connection.exists(key_with_prefix):
            result = self.connection.get(key_with_prefix)
            if result == task:
                return True
            else:
                return False
        else:
            return False

    #清除文件名key对应的task编号，在文件所有分片上传完成后被调用
    def _delete_upload_task_by_key(self,key):
        key_with_prefix = self.task_prefix + key
        self.connection.delete(key_with_prefix)
    #--------------------------------------------------------------------------------#

    #------------------------------分片处理函数---------------------------------------#
    #将上传的文件分片信息记录到redis中，该记录以list进行保存，list的每个内容为分片的文件名，在上传彻底结束后，该list还有有一个"success"的内容
    def append_clip_upload_partial_status_of_key(self, key, clip_name):
        key_with_prefix = self.upload_prefix + key
        #self.connection.lpush(key_with_prefix, clip_name)
        self.connection.sadd(key_with_prefix, clip_name)

    #分片上传完成后，将成功的信息记录在key对应的分片列表中，该函数在文件分片全部上传完成后被调用
    def append_clip_upload_success_status_of_key(self, key):
        key_with_prefix = self.upload_prefix + key
        #self.connection.lpush(key_with_prefix,"success")
        self.connection.sadd(key_with_prefix, "success")

        self._delete_upload_task_by_key(key)

    #清除key对应的分片列表的内容，该函数在分片文件合并完成后被调用,或者当文件上传失败，被分片清理程序调用
    def clear_clip_upload_status_list_of_key(self, key):
        key_with_prefix = self.upload_prefix + key
        self.connection.delete(key_with_prefix)

    #该key对应的文件是否正在合并，根据判断其集合是否含有名字叫'success'的内容，如果不存在说明文件还在上传阶段或上传发生了失败
    def is_key_contents_in_merge_status(self, key):
        key_with_prefix = self.upload_prefix + key
        if self.connection.sismember(key_with_prefix, "success"):
            return True
        else:
            return False

    #对应key的已上传文件列表，如果上传成功则含有"success"
    def get_clip_upload_status_list_of_key(self, key):
        key_with_prefix = self.upload_prefix + key
        return list(self.connection.smembers(key_with_prefix))

    def get_clip_upload_status_list_length_of_key(self, key):
        key_with_prefix = self.upload_prefix + key
        return self.connection.scard(key_with_prefix)-1          #success is not count

    #获取上传失败任务对应的文件分片,使用yield的方式进行返回，每次返回一个分片
    def get_upload_failure_key_list(self):
        key_with_prefix = self.upload_prefix + "*"
        matched_upload_key_with_prefix_list = self.connection.keys(pattern=key_with_prefix)
        #logger.info(matched_upload_key_with_prefix_list)
        upload_failure_key_without_prefix_list = []
        begin = len(self.upload_prefix)
        for item_with_upload_prefix in matched_upload_key_with_prefix_list:
            key = item_with_upload_prefix[begin:]
            #如果key对应的value的set中含有sucess，则说明该文件正处于合并状态，则不删除分片
            if self.connection.sismember(item_with_upload_prefix,"success"):
                continue
            #如果key对应的还在task中，则说明还处在上传状态,则不删除分片
            key_with_task_prefix = self.task_prefix + key
            if self.connection.exists(key_with_task_prefix):
                continue
            #key对应的内容既不再上传状态，也不在合并状态，一定是此前上传失败的任务，把该任务进行记录，并删除所有分片
            #if item_with_prefix.startswith(self.file_prefix):
            #    upload_name_without_prefix = item_with_prefix[begin:]
            #key = item_with_upload_prefix[begin:]
            upload_failure_key_without_prefix_list.append(key)

        #logger.info("Find upload failure task {} in Database.get_upload_failure_key_list() ".format(matched_upload_key_with_prefix_list))
        return upload_failure_key_without_prefix_list

        '''
        for item_with_prefix in upload_name_failure_with_prefix_list:
            print(item_with_prefix)
            item_file_clip_list = list(self.connection.smembers(item_with_prefix))
            key = item_with_prefix[begin:]
            key_with_task_prefix = self.task_prefix + key
            self._delete_upload_task_by_key(key_with_task_prefix)
            print(item_file_clip_list)
            for clip_name in item_file_clip_list:
                yield clip_name
        '''
        #matched_file_name_without_prefix_lit = []
    #--------------------------------------------------------------------------------#

    #-------------------------------------文件下载处理函数-----------------------------#
    '''
    #根据传入的文件名key，生成下载任务的task，并根据key和task来生成下载链接
    def get_download_task_by_key(self, key, realname=None):
        if realname==None:
            realname = key
        key_with_prefix = self.download_prefix + key
        task = str(uuid4().hex)

        if self.connection.exists(key_with_prefix):
            result_dict = json.loads(self.connection.get(key_with_prefix))
            task = result_dict['task']
            #用户可能多次生成下载链接，每次下载链接生成使用的realname有可能不相同，因此如果用户修改了该值，则要将realname的信息保存到数据库中
            #这样当用户再次下载时显示的文件名就是新设置的realname，而不是最近一次设置的名字
            if result_dict['realname']!=realname:
                download_task_value = {'task': task, 'realname': realname}
                self.connection.set(key_with_prefix, json.dumps(download_task_value))
            return task

        download_task_value = {'task':task, 'realname':realname}
        self.connection.set(key_with_prefix,json.dumps(download_task_value))
        self.connection.expire(key_with_prefix,timedelta(hours =1))
        return task
    '''
    #检验下载链接的key和task是否有效
    '''
    def is_download_task_valid(self,key,task):
        key_with_prefix = self.download_prefix + key
        if self.connection.exists(key_with_prefix):
            result_str = self.connection.get(key_with_prefix)
            result_dict = json.loads(result_str)
            if result_dict['task'] == task:
                return True
            else:
                return False
        else:
            return False
    '''

    #获取用户设置的下载文件名,用户获取某个文件的下载链接时，可以制定一个名字'realname'该名字再用户下载时作为保存的文件名存在，如果不设置则realname于key相同
    def get_download_realname_by_key(self,key):
        key_with_prefix = self.download_prefix + key
        if self.connection.exists(key_with_prefix):
            result_str = self.connection.get(key_with_prefix)
            result_dict = json.loads(result_str)
            return result_dict['realname']
        else:
            raise MessageException('the key not exist in')


    #查看key是否处在下载状态，即文件是否生成过下载链接，这个下载链接会在redis中保存一段时间
    #def is_key_in_downloading_status(self,key):
    #    key_with_prefix = self.download_prefix + key
    #    if self.connection.exists(key_with_prefix):
    #        return True
    #    else:
    #        return False
    #---------------------------------------------------------------------------------#

    # -------------------------------------文件列表函数--------------------------------#
    #当文件上传完成，将文件加入文件列表中，此时文件仍然可能是以分片形式存在的
    def add_to_downloadable_file_list_by_key(self, key):
        ##key_with_prefix = self.file_prefix + key
        ##self.connection.set(key_with_prefix, DownloadFileStatus.PRESENT)
        file_list_key = self.file_list_key
        self.connection.hset(file_list_key, key ,DownloadFileStatus.PRESENT)


    #从缓存中删除某个文件,由于文件可能处于合并状态，因此先将文件从浏览列表中删除，并加入待删除文件列表，待后台进程定期删除该文件
    def delete_downloadable_file_list_by_key(self, key):

        file_list_key = self.file_list_key
        if not self.connection.hexists(file_list_key, key):
            raise MessageException("file not exist")
        self.connection.hdel(file_list_key, key)
        file_deleting_list_key = self.file_deleting_list_key
        self.connection.hset(file_deleting_list_key, key, DownloadFileStatus.PRESENT)


    #检查是否在可下载文件列表中
    def is_download_file_by_key(self,key):
        file_list_key = self.file_list_key
        if self.connection.hexists(file_list_key, key):
            return True
        else:
            return False


    #获得待删除的文件列表
    def get_deleting_file_list(self):
        file_deleting_list_key = self.file_deleting_list_key
        return self.connection.hkeys(file_deleting_list_key)

    #从待删除文件列表中删除某个key
    def delete_file_from_deleting_file_list_by_key(self, key):
        file_deleting_list_key = self.file_deleting_list_key
        return self.connection.hdel(file_deleting_list_key, key)

    #返回缓存的文件列表
    def get_file_list_cache(self):
        file_list_key = self.file_list_key
        return self.connection.hkeys(file_list_key)
    # ---------------------------------------------------------------------------------#





