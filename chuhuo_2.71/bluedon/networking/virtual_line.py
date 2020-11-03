#!/usr/bin/env/python
# *-* coding: utf-8 *-*

# Copyright (C) 1998-2015 Bluedon. All Rights Reserve
# This file is part of Bluedon Firewall

import db.tables
from networking import net_cmd
from networking import ihandler
from db.mysqlconnect import mysql_connect_dict
import sys
import json

class virtual_line(ihandler.ihandler):
    def handle_cmd(self, argvs):
        if len(argvs) != 2:
            return False
        ifaceins = db.tables.convert_virtual_line_arg(argvs[1])
        return virtual_line.config(argvs[0], ifaceins)

    @staticmethod
    def config(option, ifaceins):
        if ifaceins.iStatus == 0:
            return net_cmd.del_virtual_line(ifaceins.sVirtualPortOne,
                                            ifaceins.sVirtualPortTwo)
        if option == 'add':

            return net_cmd.add_virtual_line(ifaceins.sVirtualPortOne,
                                     ifaceins.sVirtualPortTwo)
        elif option == 'enable':
            return net_cmd.edit_virtual_line(ifaceins.sVirtualPortOne,
                                     ifaceins.sVirtualPortTwo)
        elif option == 'del':
            return net_cmd.del_virtual_line(ifaceins.sVirtualPortOne,
                                     ifaceins.sVirtualPortTwo)

        return False

def recover():

    if len(sys.argv) == 1:
        return
    cur = mysql_connect_dict()
    virtualline_sql='select * from m_tbvirtualline where iStatus=1'
    cur.execute(virtualline_sql)
    virtualline_info=cur.fetchall()
    for virtualline_data in virtualline_info:
        virtualline_tmp=[]
        if sys.argv[1]=='factory_recover':
            virtualline_tmp.append('del')
            virtualline_tmp.append(json.dumps(virtualline_data))
            virtual_line().handle_cmd(virtualline_tmp)
        if sys.argv[1]== 'boot_recover':
            virtualline_tmp.append('add')
            virtualline_tmp.append(json.dumps(virtualline_data))
            virtual_line().handle_cmd(virtualline_tmp)
    cur.close()

if __name__=='__main__':
    recover()




