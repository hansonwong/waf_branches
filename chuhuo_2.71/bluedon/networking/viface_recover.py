#!/usr/bin/env python
# -*- coding:utf-8 -*-

from networking.config_iface import IfaceAddress
from networking.devices import get_physical_ifaces
from db.mysql_db import select


nic_config_info = select('select * from m_tbnetport')
physical_ifaces = get_physical_ifaces()

for i in nic_config_info:
    if i['sPortName'] not in physical_ifaces:
        IfaceAddress(i).config()
