#!/usr/bin/env python

import socket
import datetime
import random


sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(('127.0.0.1',2003))

now=datetime.datetime.now()
oneday_timedelta=datetime.timedelta(days=1)
oneday=now-oneday_timedelta
minute=datetime.timedelta(minutes=1)

for i in range(1440):
    oneday=oneday+minute
    s1=' test.http_200 %d %s\n' %(random.randint(80,100),oneday.strftime('%s'))
    s2=' test.http_200 %d %s\n' %(random.randint(60,70),oneday.strftime('%s'))
    sock.send(s1)
    sock.send(s2)
