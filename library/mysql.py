#!/usr/bin/env python

from ConfigParser import ConfigParser
import os

class MYSQLDConfig(ConfigParser):
    def __init__(self,config,**kw):
        ConfigParser.__init__(self,allow_no_value=True)
        self.config=config
        self.mysqld_vars={}
        if os.path.exists(self.config):
            self.read(self.config)
            self.get_mysqld_vars()
        else:
            self.get_defaults_mysqld_vars()
        self.set_mysqld_vars(kw)

    def set_mysqld_vars(self,kw):
        for k,v in kw.items():
            setattr(self,k,v)
            self.mysqld_vars[k]=v

    def get_mysqld_vars(self):
        rst={}
        options=self.options('mysqld')
        for i in options:
            rst[i]=self.get('mysqld',i)
        self.set_mysqld_vars(rst)

    def get_defaults_mysqld_vars(self):
        defaults={
            'datadir':'/var/lib/mysql',
            'socket':'/var/lib/mysql/mysql.sock',
            'user':'mysql',
            'symbolic-links':'0',
            'port':'3306',
            'skip-locking':None,
            'key_buffer_size':'256M',
            'max_allowed_packet':'1M',
            'table_open_cache':'256',
            'sort_buffer_size':'1M',
            'read_buffer_size':'1M',
            'read_rnd_buffer_size':'4M',
            'myisam_sort_buffer_size':'64M',
            'thread_cache_size':'8',
            'query_cache_size':'16M',
            'thread_concurrency':'8',
            'log-bin':'mysql-bin',
            'binlog_format':'mixed',
            'server-id':'1'
            } 
        self.set_mysqld_vars(defaults)            

    def set_vars(self,k,v):
        self.mysqld_vars[k] = v

    def save(self):
        if not self.has_section('mysqld'):
            self.add_section('mysqld')
        for k,v in self.mysqld_vars.items():
            self.set('mysqld',k,v)
        with open(self.config,'w') as fd:
            self.write(fd)

if __name__=='__main__':
    mc=MYSQLDConfig('/tmp/my2.cnf',max_connections=200)
    mc.set_vars('port',3306)
    mc.save()
    print mc.max_connections
    print mc.port
    print mc.socket
