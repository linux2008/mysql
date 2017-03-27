#!/usr/bin/env python

import datetime
import sys
import socket
import time
from filereversed import *

MONTH={
      'Jan':1,
      'Feb':2,
      'Mar':3,
      'Apr':4,
      'May':5,
      'Jun':6,
      'Jul':7,
      'Aug':8,
      'Sep':9,
      'Oct':10,
      'Nov':11,
      'Dec':12
}

def parseLogtime(s):
    day,month,yearandtime=s.split('/')
    year,hour,minute,second=[int(i) for i in yearandtime.split(':')]
    return datetime.datetime(year,MONTH[month],int(day),hour,minute)


def countDict(k,d):
    if k in d:
       d[k]+=1
    else:
       d[k]=1

def datacount(s):
    dic={}
    for k,v in s.items():
        if v > 10:
            dic[k]=v
    return dic 

def parseLogfile(f):
    dict={}
    now=datetime.datetime.now()
    ten_m_ago=now-datetime.timedelta(minutes=3360)
    for line in filerev(f):
        code=line.split()[8]
        timestr=line.split()[3][1:]
        key=code + '' + timestr[:-3]
        logtime=parseLogtime(timestr)
        if logtime >= ten_m_ago:
            countDict(logtime,dict)
        else:
            break
    print dict
    return dict


def send_graphite(dic):
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host = '127.0.0.1'
    port = 2003
    sock.connect((host,port))
    for k,v in dic.items():
        code,timestr=k.split()
        ts=parseLogtime(timestr+':00')
        path="httpd.%s" % code
        s='%s %d %s\n' %(path,v,ts.strftime('%s'))
        sock.send(s)

if __name__=='__main__':
    try:
        logfile=sys.argv[1]
    except IndexError:
        print '%s follow a arguement '% __file__
        sys.exit()   
    while True:
        data=parseLogfile(logfile)
        send_graphite(data)
        print '##'*10
        print datetime.datetime.now()
        time.sleep(10)

