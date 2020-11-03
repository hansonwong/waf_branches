#!/usr/bin/env python
# -*- coding: utf-8 -*-
# created by wpx 2016-04-22

import time

class Systeminfo:
	# 内存信息
    def memory_stat(self, keylist=["MemTotal", "MemFree" , "MemUsed", "MemUse"]):
        temp_mem = {}
        mem = {}
        for line in  open("/proc/meminfo", "r"):
            if len(line) < 2: continue
            name = line.split(':')[0]
            var = line.split(':')[1].split()[0]
            temp_mem[name] = long(var) * 1.0
        temp_mem["MemUsed"] = temp_mem["MemTotal"] - temp_mem["MemFree"]
        temp_mem["MemUse"] = temp_mem["MemUsed"] / temp_mem["MemTotal"]
        for k in keylist:
            mem[k] = temp_mem[k]
        return mem

	# CPU信息
    def cpu_stat(self):
        cpu = []
        cpuinfo = {}
        for line in open("/proc/cpuinfo", "r"):
            if line == '\n':
                cpu.append(cpuinfo)
                cpuinfo = {}
            if line < 2 or len(line.split(":")) < 2 : continue
            name = line.split(":")[0].rstrip()
            var = line.split(":")[1].rstrip('\n')
            cpuinfo[name] = var
        return cpu    

    # 负载信息
    def load_stat(self):
        loadavg = {}  
        f = open("/proc/loadavg")  
        con = f.read().split()  
        f.close()  
        loadavg['lavg_1']=con[0]  
        loadavg['lavg_5']=con[1]  
        loadavg['lavg_15']=con[2]  
        loadavg['nr']=con[3]  
        loadavg['last_pid']=con[4]  
        return loadavg 
    
    # 运转时间
    def uptime_stat(self):
        uptime = {}
        f = open("/proc/uptime")
        con = f.read().split()  
        f.close()  
        all_sec = float(con[0])  
        MINUTE,HOUR,DAY = 60,3600,86400  
        uptime['day'] = int(all_sec / DAY )  
        uptime['hour'] = int((all_sec % DAY) / HOUR)  
        uptime['minute'] = int((all_sec % HOUR) / MINUTE)  
        uptime['second'] = int(all_sec % MINUTE)  
        uptime['Free rate'] = float(con[1]) / float(con[0])  
        return uptime      
    
    # 获取网卡流量信息 /proc/net/dev
    # 返回dict,单位byte
    def net_stat(self):  
        net = []  
        f = open("/proc/net/dev")  
        lines = f.readlines()  
        f.close()  
        for line in lines[2:]:  
            con = line.split()  
            """ 
            intf = {} 
            intf['interface'] = con[0].lstrip(":") 
            intf['ReceiveBytes'] = int(con[1]) 
            intf['ReceivePackets'] = int(con[2]) 
            intf['ReceiveErrs'] = int(con[3]) 
            intf['ReceiveDrop'] = int(con[4]) 
            intf['ReceiveFifo'] = int(con[5]) 
            intf['ReceiveFrames'] = int(con[6]) 
            intf['ReceiveCompressed'] = int(con[7]) 
            intf['ReceiveMulticast'] = int(con[8]) 
            intf['TransmitBytes'] = int(con[9]) 
            intf['TransmitPackets'] = int(con[10]) 
            intf['TransmitErrs'] = int(con[11]) 
            intf['TransmitDrop'] = int(con[12]) 
            intf['TransmitFifo'] = int(con[13]) 
            intf['TransmitFrames'] = int(con[14]) 
            intf['TransmitCompressed'] = int(con[15]) 
            intf['TransmitMulticast'] = int(con[16]) 
            """  
            intf = dict(  
                zip(  
                    ( 'interface','ReceiveBytes','ReceivePackets',  
                      'ReceiveErrs','ReceiveDrop','ReceiveFifo',  
                      'ReceiveFrames','ReceiveCompressed','ReceiveMulticast',  
                      'TransmitBytes','TransmitPackets','TransmitErrs',  
                      'TransmitDrop', 'TransmitFifo','TransmitFrames',  
                      'TransmitCompressed','TransmitMulticast' ),  
                    ( con[0].rstrip(":"),int(con[1]),int(con[2]),  
                      int(con[3]),int(con[4]),int(con[5]),  
                      int(con[6]),int(con[7]),int(con[8]),  
                      int(con[9]),int(con[10]),int(con[11]),  
                      int(con[12]),int(con[13]),int(con[14]),  
                      int(con[15]),int(con[16]), )  
                )  
            )  
      
            net.append(intf)  
        return net 
    
    #获取网卡网速
    #单位m/s
    def net_flow(self):
        net = {}
        old_net_info = self.net_stat()
        time.sleep(1)
        net_info = self.net_stat()
        net_names = []
        for old_info in old_net_info:
            net[old_info["interface"]] = old_info["ReceiveBytes"]
        for info in net_info:
            net[info["interface"]] = (info["ReceiveBytes"] - net[info["interface"]]) / 1024.0 /1024
        return net
    
    # 磁盘空间使用
    def disk_stat(self):  
        import psutil
        hd={"total": 0,
            "used": 0,
            "free": 0}  
        parts = psutil.disk_partitions() 
        for part in parts:
            disk = psutil.disk_usage(part.mountpoint)
            hd["total"] += disk.total
            hd["used"] += disk.used
            hd["free"] += disk.free
        hd["use"] = float(hd["used"] ) / float(hd["total"])
        return hd   

    def top_stat(self):
        import os
        var = os.popen('top -b -n 2 -d 0.02').read()
        return var

if __name__ == "__main__":
    #print Systeminfo().memory_stat()
    #print Systeminfo().cpu_stat()
    #print Systeminfo().disk_stat()
    #print Systeminfo().top_stat()
    print Systeminfo().net_flow()
