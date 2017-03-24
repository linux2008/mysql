#!/usr/bin/env python

import socket
import time

def flow(f):
    dic={}
    with open(f) as fd:
       data=fd.readlines()
       data= data[3:]
       for line in data:
           dev=line.split(':')[0].strip()
           rex=line.split(':')[1].split()[0]
           outx=line.split(':')[1].split()[0]
           dic[dev]={'in':int(rex),'out':int(outx)}
    return dic

def cal(f,delay):
    data={}
    dic1=flow(f)
    time.sleep(delay)
    ts=time.time()
    dic2=flow(f)
    for k,v in dic2.items():
        int2=v['in']
        out2=v['out']
        data[k]={'in':int2-dic1[k]['in'],'out':out2-dic1[k]['out']}
    return data,ts



def send_graphite(sock,data,ts):
    for k,v in data.items():
        s1='interface.%s %d %s\n' %(k,v['in'],ts)
        s2='interface.%s %d %s\n' %(k,v['in'],ts)
        sock.send(s1+s2)



if __name__=='__main__':
   fn='/proc/net/dev'
   sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
   sock.connect(('127.0.0.1',2003))
   while True:
       data,ts=cal(fn,10)
       send_graphite(sock,data,ts)
   

