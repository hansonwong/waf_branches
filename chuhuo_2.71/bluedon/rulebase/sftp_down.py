#!/usr/bin/env python
# coding=utf-8

import os
import paramiko
from ftplib import FTP

SFTP_HOST = '172.16.6.19'
SFTP_PORT = 22
# FTP_HOST = '183.62.251.45'
# FTP_PORT = '10021'
SFTP_REMOTE_PATH = '/var/vsftpd_root/bluedon/'
SFTP_DOWN_PATH = '/tmp/ftp_down'

SFTP_USER = 'cat'
SFTP_PSWD = '123'


def sftp_down(filename=None, host=SFTP_HOST, port=SFTP_PORT, uname=SFTP_USER, pw=SFTP_PSWD):

    if not os.path.exists(SFTP_DOWN_PATH):
        os.system('mkdir -p %s' % SFTP_DOWN_PATH)

    # ftp = FTP()
    # ftp.set_debuglevel(0)
    # ftp.connect(FTP_HOST, FTP_PORT)
    # ftp.login(ftp_user, ftp_pswd)
    transport = paramiko.Transport((host, port))
    transport.connect(username=uname, password=pw)

    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.chdir(SFTP_REMOTE_PATH)

    flist = list()
    if filename is None:
        for fname in sftp.listdir():
            remote_file = os.path.join(SFTP_REMOTE_PATH, fname)
            tmp_file = os.path.join(SFTP_DOWN_PATH, fname)
            # download file
            sftp.get(remote_file, tmp_file)
            # ftp.retrbinary('RETR %s' % fname, open(tmp_file, 'wb').write)
            flist.append(tmp_file)

    else:
        remote_file = os.path.join(SFTP_REMOTE_PATH, filename)
        tmp_file = os.path.join(SFTP_DOWN_PATH, filename)
        # download file
        sftp.get(remote_file, tmp_file)
        # ftp.retrbinary('RETR %s' % filename, open(tmp_file, 'wb').write)
        flist.append(tmp_file)


    # ftp.set_debuglevel(0)
    # ftp.quit()

    sftp.close()
    transport.close()

    return flist


def sftp_get_filelist(host=SFTP_HOST, port=SFTP_PORT, uname=SFTP_USER, pw=SFTP_PSWD):
    # ftp = FTP()
    # ftp.set_debuglevel(0)
    # print host
    # print port 
    # ftp.connect(host, int(port))
    # ftp.login(ftp_user, ftp_pswd)

    # l = ftp.nlst()

    # ftp.set_debuglevel(0)
    # ftp.quit()

    transport = paramiko.Transport((host, port))
    transport.connect(username=uname, password=pw)

    sftp = paramiko.SFTPClient.from_transport(transport)

    sftp.chdir(SFTP_REMOTE_PATH)

    l = sftp.listdir()

    sftp.close()
    transport.close()

    return l



if __name__ == '__main__':
    sftp_down()
    # print sftp_get_filelist()
