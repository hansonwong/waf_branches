#!/usr/bin/env python
#-*-encoding:UTF-8-*-



import random
import socket
from  threading import Thread
import threading
import time

class send_udp_thread(threading.Thread):
    
    
    def __init__(self, ip):
        threading.Thread.__init__(self)
        self.ip = ip
        self.go = True
    #end def
    
    def stop(self):
        self.go = False
    #end def
     
    def run(self):
        
        
        while self.go:
            import socket, sys
    
    
            # 使用SOCK_DGRAM 报文
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                port = int(int(random.randint(2, 10000)))
            except ValueError:
                # 使用UDP协议
                port = socket.getservbyname(int(random.randint(2, 10000)), 'udp')
               
            s.connect((self.ip, port))
            s.sendall("Yxlink Network Vulnerability Scan System - " + str(time.time()))
            s.sendall("Yxlink Network Vulnerability Scan System - " + str(time.time()))
            s.sendall("Yxlink Network Vulnerability Scan System - " + str(time.time()))
            s.sendall("Yxlink Network Vulnerability Scan System - " + str(time.time()))
            s.sendall("Yxlink Network Vulnerability Scan System - " + str(time.time()))
            s.sendall("Yxlink Network Vulnerability Scan System - " + str(time.time())) 
            s.sendall("Yxlink Network Vulnerability Scan System - " + str(time.time()))
            s.close()
            #time.sleep(int(random.randint(1,2)))
            time.sleep(random.random())
            #time.sleep(1)
        #end while
            
    #end def
#end class
     
