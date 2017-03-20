#!/usr/bin/python 

import MySQLdb

key=[
    "Slave_IO_State",
    "Master_Host",
    "Master_User",
    "Master_Port",
    "Connect_Retry",
    "Master_Log_File",
    "Read_Master_Log_Pos",
    "Relay_Log_File",
    "Relay_Log_Pos",
    "Relay_Master_Log_File",
    "Slave_IO_Running",
    "Slave_SQL_Running",
    "Replicate_Do_DB",
    "Replicate_Ignore_DB",
    "Replicate_Do_Table",
    "Replicate_Ignore_Table",
    "Replicate_Wild_Do_Table",
    "Replicate_Wild_Ignore_Table",
    "Last_Errno",
    "Last_Error",
    "Skip_Counter",
    "Exec_Master_Log_Pos",
    "Relay_Log_Space",
    "Until_Condition",
    "Until_Log_File",
    "Until_Log_Pos",
    "Master_SSL_Allowed",
    "Master_SSL_CA_File",
    "Master_SSL_CA_Path",
    "Master_SSL_Cert",
    "Master_SSL_Cipher",
    "Master_SSL_Key",
    "Seconds_Behind_Master",
    "Master_SSL_Verify_Server_Cert",
    "Last_IO_Errno",
    "Last_IO_Error",
    "Last_SQL_Errno",
    "Last_SQL_Error",
]

conf={
    'master':'127.0.0.1:3306',
    'slave':['127.0.0.1:3307',
             '192.168.0.100:3307',
             '192.168.133.129:3307']
      }

def checkSlaveStatus(host,port):
    try:
        conn=MySQLdb.connect(host=host,port=port,user='root',connect_timeout=2)
    except Exception,e:
        print e
        return False
    cur=conn.cursor()
    cur.execute('show slave status')
    data=cur.fetchall()
    data=dict(zip(key,data[0]))
    if data["Slave_IO_Running"]== 'No' or data["Slave_SQL_Running"] == 'No':
        return False
    if data['Seconds_Behind_Master']>2:
        return False
    return True

def parseIP(s):
    host,port=s.split(':')
    return host,int(port)
    

if __name__=='__main__':
    for ip in conf['slave']:
        host,port =parseIP(ip)
        print checkSlaveStatus(host,port)
