import os, re, sys

rexplogstart = re.compile(r'grep logstart.pl')
rexpwebvisit = re.compile(r'grep webvisit.pl')

def checklogstart():
    if not os.path.exists("/usr/local/bdwaf/logs_bridge/data"):
        os.popen("mkdir -p /usr/local/bdwaf/logs_bridge/data")
    if not os.path.exists("/usr/local/bdwaf/logs_proxy/data"):
        os.popen("mkdir -p /usr/local/bdwaf/logs_proxy/data")
    flag = 0
    pfp = os.popen('ps ax | grep logstart.pl')
    lines = pfp.readlines()
    for line in lines:
        match = rexplogstart.search(line)
        if match:
            flag += 1
    if flag >= len(lines):
        os.system('/usr/local/bluedon/monitor/sbin/logstart.pl')

def checkwebvisit():
    flag = 0
    pfp = os.popen('ps ax | grep webvisit.pl')
    lines = pfp.readlines()
    for line in lines:
        match = rexplogstart.search(line)
        if match:
            flag += 1
    if flag >= len(lines):
        os.system('/usr/local/bluedon/monitor/sbin/webvisit.pl')

if __name__ == '__main__':
    checklogstart()
    checkwebvisit()
