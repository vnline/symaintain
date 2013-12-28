#!-*- coding=utf-8 -*-
import os
import redis
import msgpack
from django.conf import settings
from mc_salt.master.lib import utils,client

def get_hosts():
    """
    获取所有主机列表
    """
    hosts = []
    cli = client.Client("*" ,role="main",timeout=120)
    ret = cli.get_host()
    for host in ret.keys():
        hosts.append(host)
    return hosts


def deliver(target,files):
    """
    文件分发函数
    """
    tmp_ret = []
    for file in files:
        if file:
            file = file.encode('utf-8')
            file_name = os.path.basename(file)
            file_path = settings.MEDIA_ROOT +'/upload/'+ file_name
            print file_path
            if not os.path.exists(file_path):
                return 0
            cli = client.Client("%s" % target ,role="node",timeout=120)
            jid = cli.node_sys.node_copy(file_path,file)
            tmp_ret.append(jid)
    result = ",".join(tmp_ret)
    return result

def hot_files(target,files):
    """
    文件分发函数
    """
    tmp_ret = []
    for file in files:
        if file:
            file = file.encode('utf-8')
            cli = client.Client("%s" % target ,role="node",timeout=120)
            jid = cli.game_tools.hot_file(file)
            tmp_ret.append(jid)
    result = ",".join(tmp_ret)
    return result

def get_file_name(files):
    """
    返回文件名
    """
    file_name = []
    for file in files:
        if file:
            file = file.encode('utf-8')
            name = os.path.basename(file)
            file_name.append(name)
    return file_name

def command(as_role,target,cmd,arg,*args,**kwargs):
    """
    执行模块功能
    """

    jid = ""
    as_role = as_role.encode('utf-8')
    target = target.encode('utf-8')
    cmd = cmd.encode('utf-8')
    arg = arg.encode('utf-8')
    try:
        cli = client.Client("%s" % target, role=as_role, timeout=120)
        if as_role == "node":
            if cmd == "ping":
                jid = cli.node_sys.ping()
            elif cmd == "hot_file":
                jid = cli.game_tools.hot_file(arg)
            elif cmd == "change_client_version":
                jid = cli.game_tools.change_client_version(arg)
        elif as_role == "main":
            if cmd == "ping":
                jid = cli.main_sys.ping()
    except:
        jid = None
    return jid

def deploy(target,online_date, online_time, deploy_name, prev_name, importdb=None, cgm=None,*args,**kwargs):
    """
    执行模块功能
    """
    jid = ""
    #add_pay = add_pay.encode('utf-8')
    if importdb == 'on':
        importdb = True
    else:
        importdb = False
    if cgm == 'on':
        cgm = True
    else:
        cgm = False
    cli = client.Client("%s" % target, role="main",timeout=120)
    print target,online_date,online_time,deploy_name,prev_name,importdb,cgm
    jid = cli.install_server.install(online_date,online_time,deploy_name,prev_name,importdb,cgm)
    return jid


class RdsTool(object):

    def __init__(self):
        """
        返回redis对象
        :param opts:
        :return:
        """
        self.opts = utils.read_config()
        self.pool = redis.ConnectionPool(db=self.opts['redis_db'],host=self.opts['redis_host'],port=int(self.opts['redis_port']),password=self.opts['password'])
        self.redis = redis.Redis(connection_pool=self.pool)

    def rds_read_all(self):
        """
        获取redis 指定数据库所有的区服ID
        """
        node_list = []
        try:
            node_list = list(self.redis.smembers("salt.db.nodes"))
        except:
            pass
        return node_list

class RdsLog(object):

    def __init__(self,db):

        self.opts = utils.read_config()
        self.opts['redis_db'] = db
        self.pool = redis.ConnectionPool(db=self.opts['redis_db'],host=self.opts['redis_host'],port=int(self.opts['redis_port']),password=self.opts['password'])
        self.redis = redis.Redis(connection_pool=self.pool)

    def all(self):
        aret = self.redis.keys()
        return aret

    def get_job_result(self,jid,node_id):
        """
        从redis直接读取jid.id的结果
        """
        ret = {}
        try:
            ret = msgpack.loads(self.redis.hget(jid,node_id))
        except:
            pass
        return ret

