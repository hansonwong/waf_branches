#!/usr/bin/env python
#-*-coding:utf-8-*-

import paramiko

def connect(host): 
    ssh = paramiko.SSHClient()  
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host,username='root',password='123456',allow_agent=True) 
        return ssh
    except:
        return None

def exec_commands(conn,cmd): 
    stdin,stdout,stderr = conn.exec_command(cmd) 
    results=stdout.read() 
    return results  

if __name__ == "__main__":
    print exec_commands(connect('172.16.2.155'), 'python /work/work/cuckoo/cuckoo.py &') 
