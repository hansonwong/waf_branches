#!/usr/bin/env python
# coding=utf-8

import os
from ftplib import FTP

FTP_HOST = '172.16.6.19'
FTP_PORT = '21'
# FTP_HOST = '183.62.251.45'
# FTP_PORT = '10021'
FTP_DOWN_PATH = '/tmp/ftp_down'

ftp_user = 'bluedon'
ftp_pswd = 'bluedon@2016'



def ftp_down(filename=None):

    if not os.path.exists(FTP_DOWN_PATH):
        os.system('mkdir -p %s' % FTP_DOWN_PATH)

    ftp = FTP()
    ftp.set_debuglevel(0)
    ftp.connect(FTP_HOST, FTP_PORT)
    ftp.login(ftp_user, ftp_pswd)

    flist = list()
    if filename is None:
        for fname in ftp.nlst():
            tmp_file = os.path.join(FTP_DOWN_PATH, fname)
            ftp.retrbinary('RETR %s' % fname, open(tmp_file, 'wb').write)
            flist.append(tmp_file)

    else:
        tmp_file = os.path.join(FTP_DOWN_PATH, filename)
        ftp.retrbinary('RETR %s' % filename, open(tmp_file, 'wb').write)
        flist.append(tmp_file)


    ftp.set_debuglevel(0)
    ftp.quit()

    return flist


def ftp_get_filelist(host, port):
    ftp = FTP()
    ftp.set_debuglevel(0)
    print host
    print port 
    ftp.connect(host, int(port))
    ftp.login(ftp_user, ftp_pswd)

    l = ftp.nlst()

    ftp.set_debuglevel(0)
    ftp.quit()

    return l



if __name__ == '__main__':
    # ftp_down()
    ftp_get_filelist(FTP_HOST, FTP_PORT)
