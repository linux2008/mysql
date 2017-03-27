#!/usr/bin/env python

import sys

def filerev(fn):
    buffer = 256
    f = open(fn)
    f.seek(0,2)
    size = f.tell()
    rem = size % buffer
    offset = max(0,size-(buffer+rem))
    count = ''
    while True:
        if offset < 0:
            yield count
            break
        else:
            f.seek(offset)
            d=f.read(buffer+rem)
            rem=0
            offset=offset-buffer
            if '\n' in d:
                for c in reversed(d):
                    if c !='\n':
                        count=c+count
                    else:
                        if count:
                            yield count
                        count=''
            else:
                count=d+count
    f.close()

a=filerev(sys.argv[1])
for i in a:
    print i
