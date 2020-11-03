#!/usr/bin/env python
# -*-coding:utf-8-*-

import os
import sys
os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')

import time
import signal
import shutil
import zipfile
import threading
from db.config import execute_sql,fetchone_sql, fetchall_sql
from utils.log_logger import rLog_dbg, rLog_err

LOG_DBG = lambda x : rLog_dbg('packet_capture', x)
LOG_ERR = lambda x : rLog_err('packet_capture', x)

DIR_PATH = '/path/to/save/file'

class PacketCapture(object):

    def __init__(self, data):

        if data == None:
            return
        self.id = int(data.get('id'))
        self.file_name = str(data.get('sname')) if data.get('sname') else str(data.get('sName'))
        self.iStatus = int(data.get('iStatus')) if data.get('iStatus') else 0

        # self.file_path = os.path.join(DIR_PATH, '%s.pcap' % self.file_name)
        if self.file_name:
            self.folder_path = os.path.join(DIR_PATH, self.file_name)
            self.zip_path = os.path.join(DIR_PATH, '%s.zip' % self.file_name)

        self.run_time = None
        self.pac_data_lst = None

    def get_packet_data(self):
        time_query = fetchone_sql("SELECT iRunTime FROM `m_tbpacket_group` WHERE id={}".format(self.id))
        self.run_time = int(time_query['iRunTime'])

        pac_datas = fetchall_sql("SELECT * FROM m_tbpacket_capture WHERE iPid={}".format(self.id))
        command_lst = [self.order_comb(each) for each in pac_datas]
        return command_lst

    def order_comb(self, data):
        if not data:
            return
        if not self.run_time:
            return

        pcap_path = os.path.join(self.folder_path, '%s.pcap' % str(data['sNameCap']))
        if not os.path.exists(pcap_path):
            os.mknod(pcap_path)
        os.system('chmod 777 %s' % pcap_path)


        port = data['sPortName']
        protocol = data['sProtocol']
        packet_num = data['iPacketNum']
        packet_capnum = data['iPacketCapNum']

        src_address = data['sAddress1']
        src_port = data['iNetmask1']
        dst_address = data['sAddress2']
        dst_port = data['iNetmask2']

        rand_address = data['sAddress3']
        rand_port = data['iNetmask3']

        capacity_cap = data['iCapacityCap']

        add_data = ""
        exits_lst = [rand_address, rand_port, src_address, src_port, dst_address, dst_port]

        if capacity_cap:
            add_data += "-C %s " % str(capacity_cap)
        if port:
            add_data += "-i %s " % str(port)
        if packet_capnum:
            add_data += "-s %s " % str(packet_capnum)
        if protocol:
            add_data += "%s " % str(protocol).lower()
            for es in exits_lst:
                if es:
                    add_data += "and "
                    break

        if rand_address:
            add_data += "host %s " % str(rand_address)
            if rand_port:
                add_data += "and port %s " % str(rand_port)
        else:
            if rand_port:
                add_data += "host and port %s " % str(rand_port)

        if rand_address or rand_port:
            add_data += "and "
        if src_address:
            add_data += "src host %s " % str(src_address)
            if src_port:
                add_data += "and src port %s " % str(src_port)
        else:
            if src_port:
                add_data += "src port %s " % str(src_port)

        if src_address or src_port:
            add_data += "and "
        if dst_address:
            add_data += "dst host %s " % str(dst_address)
            if dst_port:
                add_data += "and dst port %s " % str(dst_port)
        else:
            if dst_port:
                add_data += "dst port %s " % str(src_port)

        ini_order = ""
        file_order = "-w %s " % pcap_path

        base_order = "timeout %s tcpdump" % self.run_time
        if packet_num and add_data:
            ini_order = "{base} {add}-c {num} {file}".format(base=base_order, add=add_data,
                                                              num=str(packet_num), file=file_order)
        elif add_data and not packet_num:
            ini_order = "{base} {add}{file}".format(base=base_order, add=add_data, file=file_order)
        elif packet_num and not add_data:
            ini_order = "{base} -c {num} {file}".format(base=base_order, num=str(packet_num), file=file_order)
        elif not add_data and not packet_num:
            ini_order = "{base} {file}".format(base=base_order, file=file_order)

        return ini_order.strip()

    def kill_command(self, command):
        inquire_pid = "pgrep -f '%s'" % command.strip()
        piddd = os.popen(inquire_pid).read()

        if piddd:
            stop_pid_lst = piddd.strip('\n').split('\n')
            if stop_pid_lst:
                # LOG_DBG('[KILL ORDER]: pid list %s' % stop_pid_lst)
                [os.kill(int(pid), signal.SIG_IGN) for pid in stop_pid_lst]
            LOG_DBG("killed pid {}".format(stop_pid_lst))

    def zipping_folder(self, output_zip, source_dir):
        """[zip process] transfer a folder to a zip (within same path)
        :param output_zip:  zip file path we need
        :param source_dir:   initiate folder file path
        """
        relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zip:
            for root, sub_dirs, files in os.walk(source_dir):
                # add directory (needed for empty dirs)
                zip.write(root, os.path.relpath(root, relroot))
                for file in files:
                    filename = os.path.join(root, file)
                    if os.path.isfile(filename):  # regular files only
                        arcname = os.path.join(os.path.relpath(root, relroot), file)
                        zip.write(filename, arcname)

    def pac_zip(self):
        if os.path.exists(self.zip_path):
            os.remove(self.zip_path)
        self.zipping_folder(output_zip=self.zip_path, source_dir=self.folder_path)
        LOG_DBG("zip completed..")
        if os.path.exists(self.folder_path):
            shutil.rmtree(self.folder_path)
            LOG_DBG("delete old folder..")

    def start(self):
        if self.iStatus == 0:
            return

        if not os.path.exists(self.folder_path):
            os.mkdir(self.folder_path)
        pack_command_lst = self.get_packet_data()

        def run_comm(com):
            os.system(com)

        # child = Process(target=run_comm)
        # child.daemon = True
        # child.start()
        thr_lst = list()
        for i in pack_command_lst:
            t = threading.Thread(target=run_comm, args=(i,))
            thr_lst.append(t)
            t.start()

        def auto_stop():
            while True:
                flag = 0
                for each_th in thr_lst:
                   if each_th.isAlive():
                       flag = 1
                if flag == 0:
                    execute_sql("UPDATE `m_tbpacket_group` SET iEndTime={end}, iFile=1 WHERE sName='{name}'".format(
                        end=int(time.time()), name=self.file_name))
                    self.pac_zip()
                    LOG_DBG("all child threads are ended..")
                    break

        check_thr = threading.Thread(target=auto_stop)
        check_thr.start()


    def stop(self):

        pack_command_lst = self.get_packet_data()
        for each_comm in pack_command_lst:
            self.kill_command(command=each_comm)
            LOG_DBG("killed this command .. %s" % each_comm)

        # execute_sql("UPDATE `m_tbpacket_group` SET iEndTime={end}, iFile=1 WHERE sName='{name}'".format(
        #     end=time.time(), name=self.file_name))
        # self.pac_zip()
        # LOG_DBG('[STOP PACKETIN...id=%d]' % self.id)
        pass


class DeleteCapture(PacketCapture):

    def __init__(self, data):
        super(DeleteCapture, self).__init__(data)

        self.run_time = int(data.get('iRunTime'))
        self.pac_data_lst = data.get('data')

    def delete(self):

        if self.iStatus == 1:
            LOG_DBG('DEL ACTION: when status=1, kill all command.')
            for pac_data in self.pac_data_lst:
                del_command = self.order_comb(pac_data)
                self.kill_command(del_command)

        time.sleep(2)
        if os.path.exists(self.folder_path):
            shutil.rmtree(self.folder_path)
            LOG_DBG('DEL ACTION: remove folder_path')
        if os.path.exists(self.zip_path):
            os.remove(self.zip_path)
            LOG_DBG('DEL ACTION: remove zip path')

def main_capture(action, args):
    if not os.path.exists(DIR_PATH):
        os.makedirs(DIR_PATH)

    LOG_DBG("action:%s" % action)

    if action in ['add', 'start', 'stop']:
        pack_obj = PacketCapture(args)
        if action == 'stop':
            pack_obj.stop()
        else:
            pack_obj.start()
    elif action == "del":
        for data in args:
            pack_obj = DeleteCapture(data=data)
            pack_obj.delete()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        pass
    elif sys.argv[1] == 'reset':
        if os.path.exists(DIR_PATH):
            os.system('rm -rf {}*'.format(DIR_PATH))
        else:
            os.makedirs(DIR_PATH)