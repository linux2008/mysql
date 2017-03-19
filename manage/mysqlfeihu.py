#!/usr/bin/python

import os
import sys
from optparse import OptionParser
from subprocess import Popen,PIPE
import shlex
import time
import MySQLdb


DIRNAME=os.path.dirname(__file__)
OPSTOOLS=os.path.abspath(os.path.join(DIRNAME,'..'))
sys.path.append(OPSTOOLS)

from library.mysql import MYSQLDConfig

MYSQL_DATA_DIR='/var/mysqlmanager/data'
MYSQL_CONF_DIR='/var/mysqlmanager/conf'
MYSQL_BACK_DIR='/var/mysqlmanager/back'
replication_user='repl'
replication_pass='123456'

def opt():
    parser=OptionParser()
    parser.add_option("-n","--name",
                       dest="name",
                       action="store",
                       default="myinstance")
    parser.add_option("-p","--port",
                       dest="port",
                       action="store",
                       default="3306")
    parser.add_option("-c","--command",
                       dest="command",
                       action="store",
                       default="check")
    options,args=parser.parse_args()
    return options,args

def _init():
    if not os.path.exists(MYSQL_DATA_DIR):
        os.makedirs(MYSQL_DATA_DIR)
    if not os.path.exists(MYSQL_CONF_DIR):
        os.makedirs(MYSQL_CONF_DIR)

def readConfs():
    import glob
    confs=glob.glob(MYSQL_CONF_DIR+'/*.cnf')
    return confs

def checkPort(conf_file,port):
    mc=MYSQLDConfig(conf_file)
    if mc.mysqld_vars['port'] ==port:
        return True
    else:
        return False

def _getDict(name,port):
    return {
           'pid-file':os.path.join(MYSQL_DATA_DIR,name,'%s.pid' %name),
           'socket':'/tmp/%s.sock' %name,
           'port':port,
           'datadir':os.path.join(MYSQL_DATA_DIR,name),
           'log-error':os.path.join(MYSQL_DATA_DIR,name,'%s.log' %name)
           }


def mysql_install(name):
    cnf=getCNF(name)
    cmd="mysql_install_db --defaults-file=%s" %cnf
    p=Popen(shlex.split(cmd),stdout=PIPE,stderr=PIPE)
    p.communicate()
    p.returncode

def getCNF(name):
    cnf=os.path.join(MYSQL_CONF_DIR,'%s.cnf' %name)
    return cnf

def setOwner(datadir):
    os.system("chown -R mysql:mysql %s" %datadir)

def mysql_run(name):
     cnf=getCNF(name)
     cmd="mysqld_safe --defaults-file=%s &" %cnf
     p=Popen(cmd,stdout=PIPE,stderr=PIPE,shell=True)
     time.sleep(2)
     p.returncode
 
def createInstance(name,port,**kw):
    cnf=getCNF(name)
    exists_conf=readConfs()
    for conf in exists_conf:
        if conf.split('/')[-1][-4] == name:
            print >>sys.stderr,"Instance: %s in exists" %name
            sys.exit(-1)
        if checkPort(conf,port):
            print >> sys.stderr,"Port:%s in exists" %port
            sys.exit(-1)
    if not os.path.exists(cnf):
        c=_getDict(name,port)
        c=c.update(kw)
        mc=MYSQLDConfig(cnf,**c)
        mc.save()
    datadir=os.path.join(MYSQL_DATA_DIR,name)
    if not os.path.exists(datadir):
        mysql_install(name) 
        setOwner(datadir)
        mysql_run(name)

def connMysql(name):
    cnf=getCNF(name)
    if os.path.exists(cnf):
        mc=MYSQLDConfig(cnf)
        port=int(mc.mysqld_vars['port'])
        host='127.0.0.1'
        user='root'
        conn=MySQLdb.connect(host=host,port=port,user=user)
        cur=conn.cursor()
        return cur

def getMyVariables(cur):
    sql='show global variables;'
    cur.execute(sql)
    data=cur.fetchall()
    return dict(data)

def diffMyVariables(name):
    dict={}
    cur=connMysql(name)
    vars=getMyVariables(cur)
    cnf=getCNF(name)
    mc=MYSQLDConfig(cnf)
    for k,v in vars.items():
        if v.isdigit() and len(v)>4:
            c="%.2f" %float(int(v)/1000) +'M'
            dict[k]=c
        if v.isalpha():
            dict[k]=v
        if v.islower():
            dict[k]=v
    for k,v in mc.mysqld_vars.items():
        k=k.replace('-','_')
        if k in vars and v !=vars[k]:
            print k,v,vars[k]

def setMyVariables(name,k,v):
    cnf=getCNF(name)
    mc=MYSQLDConfig(cnf)
    mc.set_vars(k,v)
    mc.save()

def runSQL(name):
    sql="grant replication slave on *.* to %s@'%%' identified by '%s'" %(replication_user,replication_pass)
    cur=connMysql(name)
    cur.execute(sql)

def changeMaster(name,host,port,user,password,logfile=None,logpos=None):
    if logfile is None:
        sql=""" change master to
                master_host='%s',
                master_port=%s,
                master_user='%s',
                master_password='%s',
             """ %(host,port,user,password)
    else:
        sql=""" change master to
                master_host='%s',
                master_port=%s,
                master_user='%s',
                master_password='%s',
                master_log_file='%s',
                master_log_pos='%s'
             """ %(host,port,user,password,logfile,logpos)
    cur=connMysql(name)
    cur.execute(sql)

def backupMysql(name):
    import datetime
    now=datetime.datetime.now()
    ts=now.strftime('%F-%m-%d %H:%M:%S')
    sqlfile=os.path.join(MYSQL_BACK_DIR,name,'%s.sql' %ts)
    dir=os.path.dirname(sqlfile)
    if not os.path.exists(dir):
        os.makedirs(dir)
    cnf=getCNF(name)
    mc=MYSQLDConfig(cnf)
    port=mc.mysqld_vars['port']
    cmd="mysqldump -A -F -x --master-data=1 --host=127.0.0.1 --port=%s --user=root > %s" %(port,sqlfile)
    p=Popen(cmd,stdout=PIPE,shell=True)
    stdin,stdout=p.communicate()
    p.returncode

def restoreMysql(name,port,sqlfile,**kw):
    createInstance(name,port,**kw)
    cnf=getCNF(name)
    mc=MYSQLDConfig(cnf)
    port=mysqld_vars['port']
    cmd='mysql -h 127.0.0.1 -uroot -p %s < %s' %(port,sqlfile)
    p=Popen(cmd,stdout=PIPE,shell=True)
    stdin,stdout=p.communicate()
    p.returncode
def findPos(s):
    import re
    rlog=re.compile(r"MASTER_LOG_FILE='(\S+)")
    rpos=re.compile(r"MASTER_LOG_POS=(\d+)")
    log=rlog.search(s)
    pos=rpos.search(s)
    if log and pos:
        return log.group(1),pos.group(1)
    else:
        return (None,None)

def getPos(sqlfile):
    with open(sqlfiel) as fd:
        for line in fd:
            log,pos=findPos(line)
            if log and pos:
                return log,pos



if __name__=='__main__':
    options,args=opt()
    _init()
    instance_name=options.name
    instance_port=options.port
    instance_cmd=options.command
    if instance_cmd =='create':
        if not args:
            createInstance(instance_name,instance_port) 
        else:
            dbtype=args[0]
            serverid=args[1]
            mysql_options={'server-id':serverid}
            if dbtype=='master':
                createIntance(instance_name,instance_port,**mysql_options)
                runSQL()
            elif dbtype=='slave': 
#                mysql_options['master-host']=args[2]
#                mysql_options['master-port']=args[3]
#                mysql_options['master-user']=replication_user
#                mysql_options['master_pass']=replication_pass
                mysql_options['skip-slave-start']=None 
                mysql_options['replicate-ignore-db']='mysql'
                createIntance(instance_name,instance_port,**mysql_options)
                host=args[2]
                port=args[3]
                user=replication_user
                password=replication_pass
                changeMaster(instance_name,host,port,user,password)

    elif instance_cmd=='check':
        diffMyVariables(instance_name)
    elif instance_cmd=='adjust':
        print args
        k=args[0]
        try:
            v = args[1]
        except IndexError:
            v = None
        setMyVariables(instance_name,k,v)
    elif instance_cmd=='backup':
        backupMysql(instance_name)
    elif instance_cmd=='restore':
        server_id=args[0]
        master_host=args[1]
        master_port=args[2]
        sqlfile=args[3]
        mysqld_options={'server_id':server_id}
        mysqld_options=['skip-slave-start'=None
        mysqld_options=['replicate-ignore-db']='mysql'
        restoreMysql(instance_name,instance_port,sqlfile,**mysqld_options)
        logfile,logpos=getPos(sqlfile)
        changeMaster(instance_name,master_host,master_port,REPLICATION_USER,REPLICATION_PASS,logfile,logpos)
