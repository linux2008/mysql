#!/usr/bin/env python

from ConfigParser import ConfigParser

class myconf(ConfigParser):
    def __init__(self,conf,**kw):
        ConfigParser.__init__(self,allow_no_value=True)
        self.conf=conf
        self.read(self.conf)
        self.var(kw)

    def var(self,kw):
        for k,v in kw.items():
            setattr(self,k,v)

if __name__=='__main__':
    mc=myconf('/tmp/mysql.cnf',connect=200)
    print mc.get('mysqld','port')
    print mc.connect
