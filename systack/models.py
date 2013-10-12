#!-*- coding=utf-8 -*-
#from django.utils import timezone
import sys,os
import redis,msgpack
from django.db import models
from mc_salt.master.lib import utils,client


# Create your models here.

class Schedule(models.Model):
    agent = models.CharField(max_length=20)
    server_name = models.CharField(max_length=20)
    open_time = models.DateTimeField(auto_now = False)
    version = models.CharField(max_length=50)
    deploy = models.BooleanField()
    created_by = models.CharField(max_length=20,blank=True)
    deployed_by = models.CharField(max_length=20)
    status = models.BooleanField()
    remark = models.TextField(max_length=200,blank=True)
    mtime = models.DateTimeField(auto_now = True)

    def __unicode__(self):
        return self.server_name
    class Meta:
        db_table = "schedule"


class Hot_update(models.Model):
    target = models.CharField(max_length=20)
    result = models.TextField(max_length=500, blank=True)
    files = models.TextField(max_length=200)
    deployed_by = models.CharField(max_length=20,blank = True)
    mtime = models.DateTimeField(auto_now = True)

    @classmethod
    def file_update(cls,target,files):
        """
        文件热更函数
        """
        send_ret = {}
        hot_ret = {}
        result_dict = {}
        cli = client.Client("%s" % target ,role="node",timeout=120)
        for file in files:
            file = file.encode('utf-8')
            file_name = os.path.basename(file)
            mod,file_ext = os.path.splitext(file_name)
            file_path = '/data/web/systack/media/upload/'+ file_name
            print file_path
            if not os.path.exists(file_path):
                return False
            send_ret[file_name] = cli.node_sys.node_copy(file_path,file)
            print send_ret
            if file_ext == ".beam":
                print "in node_hot"
                hot_ret[file_name] = cli.gstools.node_hot('hot_update',mod)
                print "already hot!",hot_ret
            else:
                pass
        for k,v in send_ret.iteritems():
            result_dict.setdefault(k,[ ]).append(v)
        print result_dict
        for k,v in hot_ret.items():
            result_dict.setdefault(k,[ ]).append(v)
        return result_dict

    @classmethod
    def get_file_name(cls,files):
        """
        返回文件名
        """
        file_name = ""
        for file in files:
            file = file.encode('utf-8')
            file_name += os.path.basename(file)

        return file_name

    class Meta:
        db_table = "hot_update"

    def __unicode__(self):
        return self.files

class RdsTool(object):

    def __init__(self,rdb):
        """
        返回redis对象
        :param opts:
        :return:
        """
        self.rdb = rdb
        self.opts = utils.read_config()
        self.pool = redis.ConnectionPool(db=self.opts['redis_db'],host=self.opts['redis_host'],port=int(self.opts['redis_port']),password=self.opts['password'])
        self.redis = redis.Redis(connection_pool=self.pool)


    def read(self,jid,id):
        """
        返回解码后的values
        """
        msg = self.redis.hget('salt.db.return',"%s.%s" % (jid,id))
        return msgpack.loads(msg,use_list=True)

    def rds_read_all(self):
        """
        获取redis 指定数据库所有的区服ID
        """
        node_id = []
        rdb_keys = self.redis.hkeys(self.rdb)
        if rdb_keys:
            for k in rdb_keys:
                if k.split('.')[1] not in node_id:
                    node_id.append(k.split('.')[1])
        return node_id


class Deploy(models.Model):
    target = models.CharField(max_length=20)
    open_time = models.DateTimeField(auto_now = False)
    deploy_name = models.CharField(max_length=20)
    prev_name = models.CharField(max_length=20)
    importdb = models.BooleanField()
    cgm = models.BooleanField()
    deployed_by = models.CharField(max_length=20)
    result = models.TextField(max_length=500, blank=True)
    mtime = models.DateTimeField(auto_now = True)

    @classmethod
    def get_job_result(cls,jid,id):
        """
        从redis直接读取jid.id的结果
        """
        rds = RdsTool()
        str_ret = rds.read("%s.%s" % (jid,id))
        return str_ret


    class Meta:
        db_table = "deploy"

    def __unicode__(self):
        return self.deploy_name

class Operation(models.Model):
    target = models.CharField(max_length=20)
    cmd = models.CharField(max_length=200)
    deployed_by = models.CharField(max_length=20)
    mtime = models.DateTimeField(auto_now = True)

    def __unicode__(self):
        return self.cmd
    class Meta:
        db_table = "operation"