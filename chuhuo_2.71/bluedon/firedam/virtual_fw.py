#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""防火墙 》 虚拟防火墙
虚拟防火墙基于docker实现，每个虚拟防火墙就是一个容器（Container），
里面包含python，php，mysql等服务
"""

import json
import sys

from db.mysql_db import update, Dict, select
from networking.nat64 import exec_cmd


def start_container(data):
    name = 'vfw%s' % data['id']  # 容器名称
    if data.get('sContainerID', ''):  # 容器不是首次新建
        _, output = exec_cmd("docker ps --filter='name={name}'".format(name=name), msg='virtualfw:')
        if name in output:  # 如果当前名称的容器已启动
            return
        # 启动容器
        exec_cmd('docker start {vm_id}'.format(vm_id=data['sContainerID']), msg='virtualfw:')
        # 将虚拟防火墙的管理口的444端口映射到物理机上
        exec_cmd('sh scripts/container_port.sh {name} {ip} {port}'.format(
            name=name, ip=data['sAddressIP'], port=data['sPort']), msg='virtualfw:')
        # 将选用的网口桥接到虚拟防火墙内
        for iface in data['sNetport'].split(','):
            exec_cmd('sh scripts/container_addiface.sh {name} {iface}'.format(
                name=name, iface=iface), msg='virtualfw:')
        # 启动容器内的开机脚本
        exec_cmd('docker exec {name} /home/init.sh'.format(name=name), msg='virtualfw:')
        # 更新容器启动状态
        update('update m_tbvirtualfw set state=1 where id=?', data['id'])
    else:
        # 新建容器
        cmd = 'docker run -itd --privileged --name={name} bd/virtualfw /bin/bash'
        exec_cmd(cmd.format(name=name), msg='virtualfw:')
        exec_cmd('sh scripts/container_port.sh {name} {ip} {port}'.format(
            name=name, ip=data['sAddressIP'], port=data['sPort']), msg='virtualfw:')
        for iface in data['sNetport'].split(','):
            exec_cmd('sh scripts/container_addiface.sh {name} {iface}'.format(
                name=name, iface=iface), msg='virtualfw:')
        exec_cmd('docker exec {name} /home/init.sh'.format(name=name), msg='virtualfw:')
        # 更新容器id，和容器启动状态
        _, vm_id = exec_cmd("docker ps --filter='name={name}' -q".format(name=name), msg='virtualfw:')
        update('update m_tbvirtualfw set state=1, sContainerID=? where id=?', vm_id, data['id'])


def del_container(data):
    """删除虚拟防火墙
    先停用再删除
    """
    name = 'vfw%s' % data['id']
    stop_container(data)
    exec_cmd('docker rm {name}'.format(name=name), msg='virtualfw:')


def stop_container(data):
    """停用虚拟防火墙"""
    name = 'vfw%s' % data['id']
    exec_cmd('sh scripts/container_port.sh {name} {ip} {port} del'.format(
        name=name, ip=data['sAddressIP'], port=data['sPort']), msg='virtualfw:')
    exec_cmd('docker stop {name}'.format(name=name), msg='virtualfw:')


def proc_virtualfw(args):
    """配置虚拟防火墙
    启用，停用，删除
    """
    data = Dict(**json.loads(args[1]))
    data.iStatus = str(data.iStatus)
    if args[0] == 'del':
        del_container(data)
    elif args[0] == 'add' and data.iStatus == '0':  # 新建时如果不启用，直接返回
        return
    elif data.iStatus == '1':
        start_container(data)
    else:
        stop_container(data)


def recover():
    if len(sys.argv) == 1:
        return
    data = select('select * from m_tbvirtualfw where iStatus=1')
    for info in data:
        if sys.argv[1] == 'factory_recover':
            info.iStatus = 0
            del_container(info)
        if sys.argv[1] == 'boot_recover':
            start_container(info)


if __name__ == '__main__':
    recover()
