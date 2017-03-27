#!/usr/bin/env python

f=open('/tmp/passwd1')
f.seek(0,2)
line=''
while True:
    if f.tell()==1:
        print line
        break
    else:
        f.seek(-2,1)
        c=f.read(1)
        if c !='\n':
            line=c+line
        else:
            print line
            line =''
