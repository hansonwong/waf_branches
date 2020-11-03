#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time,datetime
import hashlib
from sysinfo_tables import WafSessionManager
from db import License,engine,Session
from logging import getLogger

key_pub = "key.pub"
key_priv = "key.priv"
aeskey="./aes.key"

def usage():
    print """
    example usage:
    #1:generate a cert,2:varify a cert,3:generate a encrypted mod rule file,option=4:initialize license table
    option=1
    #when option=1,file means the output encpyted cert file, the default value is bdwaf.license
    #while option=2,means the encrypted cert file
    #while option=3,means the file to be encrypted,it must be a tar file
    file=bdwaf.license
    
    #note:feilds beneath are only need when option=1,and only serial is prerequisite,others are optional
    #0:free,1:official,when free, serial and expire are needed too.
    free=1
    serial=aaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    expire="2010-01-01 00:00:00"
    name=蓝盾信息安全技术有限责任公司
    addr=黄埔大道西御发商务中心6楼
    email=yzg@chinabluedon.cn
    tel=18000000000
    """
def write_license(msgdic,filename):
    #write license msgs to a file
    if os.path.isfile(filename):
        os.remove(filename)
    file = open(filename,"wb")
    file.write(str(msgdic))
    file.close()

def enryptRSA(filein,fileout):
    cmdstr = "openssl rsautl -encrypt -in %s -inkey %s -pubin -out %s" % (filein,key_pub,fileout)
    os.system(cmdstr)
    
def decryptRSA(filein,fileout):
    cmdstr = "openssl rsautl -decrypt -in %s -inkey %s -out %s" % (filein,key_priv,fileout)
    os.system(cmdstr)
    
def getSerial():
    fdisk = ""
    try:
        fdisk = os.popen('/usr/sbin/hwinfo --disk | grep "Serial ID"')
    except:
        pass
    strdiskid = ""
 
    for line in fdisk:
        strlist = line.strip().split(":")
        if not strlist:
            continue
        if strlist[0].lower() != "serial id":
            continue
        strdiskid = strlist[1].strip().replace("\"","")
        break
    fdisk.close()
    #print strdiskid

    #get the first mac addr, the first means eth0
    from uuid import getnode as get_mac
    mac = get_mac()
    strmac = str(mac)

    m = hashlib.md5()
    m.update(strdiskid + strmac)

    return m.hexdigest()

def varify_cert(filein):
    fileout = filein+".out"
    decryptRSA(filein,fileout)

    file = open(fileout)
    msg = file.read()
    certmsg = eval(msg)

    localt = time.localtime()
    datenow = datetime.datetime.fromtimestamp(time.mktime(localt))
    #strtime = "%4d-%2d-%2d %2d:%2d:%2d" % (localt.tm_year,localt.tm_mon,localt.tm_mday,localt.tm_hour,localt.tm_min,localt.tm_sec)

    serial = getSerial()
    free = certmsg.get("free","1")
    certserial = certmsg.get("serial","")
    certdate   = certmsg.get("expire","")
    dateobj = datetime.datetime.strptime(certdate, "%Y-%m-%d %H:%M:%S")
    certtime = time.strptime(certdate, "%Y-%m-%d %H:%M:%S")
    #if free == "0":
        #print "free"
        #return True
    #    pass 			#to write to database
    if certserial != serial:
        print "serial false"
        getLogger("main").error("serial invalid")
        return False
    if dateobj < datenow:
        getLogger("main").error("date invalid")
        return False

    os.remove(fileout)
    company=certmsg.get("name","")
    address=certmsg.get("addr","")
    email=certmsg.get("email","")
    telephone=certmsg.get("tel","")
    lcs = License()
    lcs.sn=serial
    lcs.vertype=int(free)
    lcs.validate=time.mktime(certtime)
    lcs.company=company
    lcs.address=address
    lcs.email=email
    lcs.telephone=telephone
    sess = WafSessionManager()
    sess.AddLicense(lcs)
    
    file.close()
    return True

def encryptModConfFile(gzin,gzout):
    #fbase = os.path.basename(gzin)
    #fgz = fbase.split(".")[0] + ".tar.gz"
    #os.system("tar cf " + fgz + " " + outfile)
    cmdstr = "openssl enc -aes-256-cbc -salt -in %s -out %s -pass file:%s" % (gzin,gzout,aeskey)
    os.system(cmdstr)

def decryptModConfFile(enced, dirout):
    """
    fbase = os.path.basename(gzin).split(".")[0]
    fout = os.path.dirname(gzin)+"/"+(fbase + "2.")+ ".".join(os.path.basename(gzin).split(".")[1:])
    decryptRSA(gzin,fout)
    ret = os.system("tar xf " + fout + " -C " + dirout)
    """
    if not dirout:
        return False

    deced = enced + ".deced"
    cmdstr = "openssl enc -d -aes-256-cbc -in %s -out %s -pass file:%s" % (enced,deced,aeskey)
    if os.system(cmdstr) != 0:
        getLogger("main").error("mod conf file invalid")
        return False

    os.system("rm -rf %s" % os.path.join(dirout, '*'))
    
    if os.system("tar xf " + deced + " -C " + dirout) != 0:
        getLogger("main").error("tar file extract false")
        #os.remove(deced)
        return False

    getLogger("main").info("mod conf file updated")
    #os.remove(deced)
    return True

def initLicenseTable():
    sess = Session()
    sess.query(License).delete()
    tmplcs = License()
    tmplcs.sn=getSerial()
    tmplcs.vertype=1
    sess.merge(tmplcs)
    sess.commit()
    sess.close()

def main():
    certdic={}
    args = sys.argv[1:]
    #show usage
    if not args:
        usage()
        print getSerial()
        return
    #parse args
    outfile = ""
    for item in args:
        tmp = item.strip().split("=")
        if tmp[0] == "file":
            outfile = tmp[1]
            continue
        if len(tmp) > 1:
            certdic[tmp[0]] = tmp[1]

    certout = ""
    if outfile:
        certout = outfile
    else:
        certout="bdwaf.license"

    free = certdic.get("free","1")
    if  certdic.has_key("option"):
        if certdic["option"] == "1" :
            certdic.pop("option")
            if free != "0":
                if not certdic.has_key("serial"):
                    print "you must input the serial"
                    return
                if not certdic.has_key("expire"):
                    print "you must input the expire"
                    return
            msgsfile = ".certtmp.license"
            
            write_license(certdic,msgsfile)
            enryptRSA(msgsfile,certout)
            
            os.remove(msgsfile)
            return
        elif certdic["option"] == "2":
            certdic.pop("option")
            varify_cert(certout)
        elif certdic["option"] == "3":
           if not outfile:
               print "no file to be encypted"
               return
           fileout=outfile+".enc"
           encryptModConfFile(outfile,fileout)
           return
        elif certdic["option"] == "4":
           initLicenseTable()

        
    
if __name__ == "__main__":
    main()
    
    
    
