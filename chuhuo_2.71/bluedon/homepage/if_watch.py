from __future__ import division
import os
import commands
import operator
import time
# from db.config import fetchall_sql

getdata = operator.itemgetter(0,1,9)
ifname = operator.itemgetter(0)
rxbyte = operator.itemgetter(1)
txbyte = operator.itemgetter(9)
getprefix = operator.itemgetter(0,1,2,3)
prefix = lambda x:''.join(getprefix(x))
ifrx = operator.itemgetter(0)
iftx = operator.itemgetter(1)
interval = 1

def interface_current_time():
    return os.stat('/proc/net/dev').st_mtime
    #return time.time()

def interface_get_traffic():
    ret = commands.getoutput('cat /proc/net/dev')
    ret = ret.split('\n')
    ret = [l.split() for l in ret]
    return {ifname(l).strip(':'):(rxbyte(l),txbyte(l))
            for l in ret if len(ifname(l)) >= 4 and prefix(ifname(l)) == 'vEth'}

def interface_flow_calc(cur,pre,t):
    cur = float(cur)
    pre = float(pre)
    t = float(t) if float(t) > 2 else 2
    if cur < pre:
        return 0
    res = (cur - pre)/t
    res = res / 1048576 * 8
    res = round(res,4) if res < 1 else round(res,2)
    return res
    pass

def interface_traffic(t_pre,last,nat,last_last):
    ifrecord = {}

    def add_unit(i):
        #return str(num) +'B/s' if num < 1024 else str(round(num/1024,2))+'KB/s' if num < 1048576 else str(round(num/1048576,2))+'MB/s'
        i = int(i)/1048576 * 8
        i = round(i,4) if i < 1 else round(i,2)
        return i



    def assign(x,y,z,dt,is_nat=False):
        """
            Description:
                x ---> interface name
                y ---> current size
                z ---> last size
                dt ---> delter time
        """
        if not last_last.has_key(x):
            last_last[x] = (0,0)

        ix0 = (int(ifrx(z)) - int(ifrx(last_last[x])))/dt
        ox0 = (int(iftx(z)) - int(iftx(last_last[x])))/dt

        ix = 0 if dt == 0 else (int(ifrx(y)) - int(ifrx(z)))/dt
        ox = 0 if dt == 0 else (int(iftx(y)) - int(iftx(z)))/dt

        if abs(ix - ix0) * 4 > ix0:
            # ix = (ix + ix0)/2
            ix = ix0 + (ix - ix0) / 4
        if abs(ox - ox0) * 4 > ox0:
            # ox = (ox + ox0)/2
            ox = ox0 + (ox - ox0) / 4

        #print '--------------------------------------------------------------'
        #print 'dt = ',dt,' ix0 = ',ix0,' ix =  ',ix,' ox0 = ',ox0,' ox = ',ox
        # ix = 0 if dt == 0 else (int(ifrx(y)) - int(ifrx(z)))/dt
        # ox = 0 if dt == 0 else (int(iftx(y)) - int(iftx(z)))/dt
        if is_nat:
            ifrecord[x] = {"IN":add_unit(ix),"OUT":add_unit(ox)}
            #print 'nat:',x,'  ',ifrecord[x]
        else:
            ifrecord[x] = {"IN":add_unit(ox),"OUT":add_unit(ix)}
            #print 'none nat:',x,' ',ifrecord[x]

        return (ix,ox)

    current = interface_get_traffic()
    t_cur = time.time()
    dt = t_cur - t_pre
    dt = 2 if dt < 2 or dt ==0 else dt

    # process all none nat interfaec
    #_ = [ assign(ifn,current[ifn],last[ifn],dt) for ifn in current
    #      if last.has_key(ifn) and current[ifn] > last[ifn]
    #      and not ifn in nat]

    for ifn in current:
        if ifn in nat:
            continue
        if last.has_key(ifn) and current[ifn] > last[ifn]:
            assign(ifn,current[ifn],last[ifn],dt)

    all_trf = [ assign(ifn,current[ifn],last[ifn],dt,is_nat=True) for ifn in current
                if last.has_key(ifn)
                and current[ifn] > last[ifn]
                and ifn in nat]

    # sum all nat flow traffic
    gin = sum([ifrx(one) for one in all_trf])
    gout = sum([iftx(one) for one in all_trf])
    ifrecord["GLOBAL"]={"IN":add_unit(gin),"OUT":add_unit(gout)}

    #print ifrecord
    import copy
    return ifrecord,copy.deepcopy(current),t_cur,copy.deepcopy(last)

def parse_iftop(path):
    with open(path,'r') as fp:
        lines = fp.readlines()
    tx,rx = 0,0
    for line in lines:
        if line.split()[0] == 'Cumulative':
            tx,rx = line.split()[2:4]
            print tx,' ',rx
            break


def if_top(ifs):
    if_top_path = '/usr/local/bluedon/log/iftop.txt'
    for i in ifs:
        os.system('iftop  -Pp -Nn -t -L 100 -s 1 -i %s > %s ' % (i,if_top_path))
        parse_iftop(if_top_path)


    pass

if __name__ == '__main__':

    #parse_iftop('./iftop.txt')
    t_pre =  interface_current_time()
    res_pre = interface_get_traffic()
    # no_traffic = {'GLOBAL':{'OUT':0.0, 'IN':0.0}}
    # result = no_traffic
    # t = t_pre
    # while True:
    #     traffic_pre = result
    #     result,res_pre,t_pre = interface_traffic(t_pre,res_pre,[])
    #     if result == no_traffic:
    #         result = traffic_pre
    #         t_pre = t
    #     else:
    #         t = t_pre
    #         traffic_pre = result
    #         print result
    #     time.sleep(interval)
