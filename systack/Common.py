#!-*- coding=utf-8 -*-
import sys,os,re
import redis
import msgpack
from mc_salt.master.lib import utils,client



def deliver(target,files):
    """
    文件分发函数
    """
    tmp_ret = []
    for file in files:
        if file:
            file = file.encode('utf-8')
            file_name = os.path.basename(file)
            file_path = '/data/web/maintain/systack/media/upload/'+ file_name
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

class RdsTool(object):

    def __init__(self,keys='salt.db.return'):
        """
        返回redis对象
        :param opts:
        :return:
        """
        self.keys = keys
        self.opts = utils.read_config()
        self.pool = redis.ConnectionPool(db=self.opts['redis_db'],host=self.opts['redis_host'],port=int(self.opts['redis_port']),password=self.opts['password'])
        self.redis = redis.Redis(connection_pool=self.pool)


    def read(self,jid):
        """
        返回解码后的values
        """
        msg = self.redis.hget(self.keys,jid)
        try:
            msg = msgpack.loads(msg,use_list=True)
        except:
            pass
        return msg


    def rds_read_all(self):
        """
        获取redis 指定数据库所有的区服ID
        """
        idset = []
        regex = r'(\d{20})\.(\w\d_.+_\w\d+)'
        rdb_keys = self.redis.hkeys(self.keys)
        if rdb_keys:
            for k in rdb_keys:
                m = re.match(regex,k)
                try:
                    id = m.group(2)
                    if id not in idset:
                        idset.append(id)
                except:
                    pass
        return idset

class Get_log(object):

    @classmethod
    def get_job_result(cls,jid,id):
        """
        从redis直接读取jid.id的结果
        """
        rds = RdsTool()
        str_ret = rds.read("%s.%s" %(jid,id))
        return str_ret