from __future__ import division
import os
import time
import psutil
import commands
from operator import itemgetter

def cpu_usage_stat():
    cpu = {'0':[],'1':[]}
    for i in range(2):
         with open('/proc/stat', 'r') as fp:
            ls = fp.readline().split()
            cpu[str(i)] = ls

            time.sleep(0.1)
    cpu1_sum,cpu0_sum  = 0,0
    for i in range(len(cpu['1'])-1):
        cpu0_sum += int(cpu['0'][i+1])
        cpu1_sum += int(cpu['1'][i+1])
    total_cpu = cpu1_sum - cpu0_sum
    idle_cpu = int(cpu['1'][4]) - int(cpu['0'][4])
    #print total_cpu,' ',idle_cpu
    cpu_usage = (total_cpu - idle_cpu)/total_cpu
    #print round(cpu_usage,3)*100
    return round(cpu_usage,3)*100

def cpu_usage_mpstat_old():
    cpu = ['all','cpu0','cpu1','cpu2','cpu3','cpu4','cpu5','cpu6','cpu7']
    info = commands.getoutput('mpstat -P ALL 1 1')
    infolist =  info.split('\n')
    cpu_n = len(infolist)//2 - 4
    cpu_usage = {}
    for i in range(cpu_n + 1):
        p_info = infolist[i+3].split()[12]
        cpu_usage[cpu[i]] = round(100 - float(p_info))
    #print (cpu_usage)
    return cpu_usage



def cpu_usage_mpstat():
    #info = commands.getoutput('mpstat -P ALL 1 1')
    #infolist =  info.split('\n')[3:]
    #infolist =  infolist[0:infolist.index('')]

    #cpus = len(infolist)
    #usage = lambda x:infolist[x].split()[12]
    #cpu_n = lambda x:infolist[x].split()[2]

    cpu_usage = {}
    #cpu_usage[cpu_n(0)] = round(100 - float(usage(0)))
    #for i in range(1,cpus):
    #    cpu_usage['cpu' + str(cpu_n(i))] = round(100 - float(usage(i)))
    ##print (cpu_usage)
    cpu_usage['all'] = psutil.cpu_percent(interval=1)
    return cpu_usage


def mem_usage():
    # with open('/proc/meminfo','r') as fp:
    #     total = int(fp.readline().split()[1])
    #     free = int(fp.readline().split()[1])
    #     available = int(fp.readline().split()[1])
    #     buffers = int(fp.readline().split()[1])
    #     cached= int(fp.readline().split()[1])
    #     #mem_usage = (total - free - buffers - cached)/total
    # mem_usage = (total - free)/total
    #print round(mem_usage*100)
    meminfo = psutil.virtual_memory()
    mem_usage = 1 - meminfo.available / meminfo.total
    return round(mem_usage*100)
    #return round(mem_usage,3)*100

def disk_usage():
    #fs = os.statvfs('/home')
    #used = fs.f_blocks - fs.f_bavail
    #usage = round(used / (used + fs.f_bavail),3)*100
    ##print round(usage)
    # du = commands.getoutput('df --total -mH  /var | grep total')
    # return int(du.split()[4].strip('%'))
    return (psutil.disk_usage('/var').percent)
    #return round(usage)
if __name__ == '__main__':
    #while 1:
    print cpu_usage_mpstat()
    #    #cpu_usage()
    print mem_usage()
    print disk_usage()
    pass
