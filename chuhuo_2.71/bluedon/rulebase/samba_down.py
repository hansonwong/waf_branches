#!/usr/bin/env python
# coding=utf-8

import os
import commands
from ftplib import FTP

# FTP_HOST = '172.16.6.19'
# FTP_PORT = '21'
FTP_HOST = '183.62.251.45'
FTP_PORT = '10021'
FTP_DOWN_PATH = '/tmp/ftp_down'

ftp_user = 'bluedon'
ftp_pswd = 'bluedon@2016'

# SMB_HOST = '172.16.6.19'
SMB_HOST = '108.61.214.131'
SMB_DOWN_PATH = '/tmp/samba_down'
SMB_USER = 'samba'
SMB_PSWD = 'samba'
SMB_PATH = 'SambaShare'



def ftp_down(filename=None):
    pass
    # if not os.path.exists(FTP_DOWN_PATH):
    #     os.system('mkdir -p %s' % FTP_DOWN_PATH)

    # ftp = FTP()
    # ftp.set_debuglevel(0)
    # ftp.connect(FTP_HOST, FTP_PORT)
    # ftp.login(ftp_user, ftp_pswd)

    # flist = list()
    # if filename is None:
    #     for fname in ftp.nlst():
    #         tmp_file = os.path.join(FTP_DOWN_PATH, fname)
    #         ftp.retrbinary('RETR %s' % fname, open(tmp_file, 'wb').write)
    #         flist.append(tmp_file)

    # else:
    #     tmp_file = os.path.join(FTP_DOWN_PATH, filename)
    #     ftp.retrbinary('RETR %s' % filename, open(tmp_file, 'wb').write)
    #     flist.append(tmp_file)


    # ftp.set_debuglevel(0)
    # ftp.quit()

    # return flist


def ftp_get_filelist(host, port):
    pass
    # ftp = FTP()
    # ftp.set_debuglevel(0)
    # print host
    # print port 
    # ftp.connect(host, int(port))
    # ftp.login(ftp_user, ftp_pswd)

    # l = ftp.nlst()

    # ftp.set_debuglevel(0)
    # ftp.quit()

    # return l


def smb_get_filelsit(host=SMB_HOST, share_path='SambaShare', user='samba', pswd='samba'):
    # smbclient cmd
    cmd = lambda x: "smbclient -c '{pcmd}' //{host}/{spath} -U {u}%{p}".format(
        pcmd=x, host=host, spath=share_path, u=user, p=pswd
    )
    cmd_ls = cmd('ls')
    print cmd_ls
    status, output = commands.getstatusoutput(cmd_ls)
    flist = list()
    for line in output.split('\n'):
        line_item = line.strip().split()
        # get filename
        if len(line_item) >= 2 and line_item[1] == 'N':
            flist.append(line_item[0])

    print flist
    return flist

def smb_downfile(filename=None, store_path=SMB_DOWN_PATH, host=SMB_HOST, share_path=SMB_PATH, user=SMB_USER, pswd=SMB_PSWD):
    if not os.path.exists(store_path):
        print('mkdir -p %s' % store_path)
        os.system('mkdir -p %s' % store_path)

    dfiles = list()
    server_files = smb_get_filelsit(host=SMB_HOST, user=SMB_USER, pswd=SMB_PSWD)
    if not server_files:
        print 'get file list error'
        return None

    cmd = lambda x: "smbclient -c '{pcmd}' //{host}/{spath} -U {u}%{p}".format(
        pcmd=x, host=host, spath=share_path, u=user, p=pswd
    )
    if filename is None: dfiles = server_files
    else:
        if filename in server_files:
            dfiles.append(filename)

    # down files from samba server
    got_files = list()
    for fname in dfiles: 
        cmd_dw = cmd('get %s' % fname)
        os.chdir(store_path)
        status, output = commands.getstatusoutput(cmd_dw)
        print output
        if str(status) == '0':
            got_files.append(fname)

    return got_files





if __name__ == '__main__':
    # ftp_down()
    # ftp_get_filelist(FTP_HOST, FTP_PORT)
    # smb_get_filelsit()
    smb_downfile()
