import sys
import subprocess
from logging import getLogger
from db.mysql_db import select

ACTION_MAP = {
    '1': 'ACCEPT',
    '2': 'DROP',
}


class NetsWithinNets(object):
    def __init__(self, data):
        for key, val in data.iteritems():
            setattr(self, key, val)
        self.iTime = int(self.iTime) * 60 if self.iTime and self.iAction == '2' else 0
        self.sIpAddressList = self.sIpAddressList.split(',') if data.get('sIpAddressList') else []

    def config(self):
        """ config rules """
        cmd = 'ipset create %s hash:net timeout %s' % (self.groupname, self.iTime)
        subprocess.call(cmd, shell=True)
        getLogger('main').info('nets_within_nets--create ipset')
        for ip in self.sIpAddressList:
            cmd = 'ipset add %s %s' % (self.groupname, ip)
            subprocess.call(cmd, shell=True)

        cmd = 'iptables -A FWFORWARD -m set --match-set {network} src -j {action}'.format(
            network=self.groupname,
            action=ACTION_MAP[self.iAction]
        )
        subprocess.call(cmd, shell=True)
        getLogger('main').info('nets_within_nets--add iptable rules')

    def enable(self):
        self._clean_up()
        self.config()

    def disable(self):
        self._clean_up()

    def _clean_up(self):
        """ clear rules """
        cmd = 'iptables -D FWFORWARD -m set --match-set {network} src -j {action}'.format(
            network=self.groupname,
            action=ACTION_MAP[self.iAction]
        )
        subprocess.call(cmd, shell=True)
        getLogger('main').info('nets_within_nets--del iptable rules')
        cmd = 'ipset destroy %s' % self.groupname
        subprocess.call(cmd, shell=True)
        getLogger('main').info('nets_within_nets--destroy ipset')

    def entry(self):
        if str(self.iStatus) == '1':
            self.enable()
        elif str(self.iStatus) == '0':
            self.disable()


def recover():
    if len(sys.argv) != 2:
        return
    sql = 'select * from m_tbnetinnet'
    result = select(sql)
    for data in result:
        data['iAction'] = str(data['iAction'])
        if sys.argv[1] == 'boot_recover':
            data['iStatus'] = str(data['iStatus'])
        elif sys.argv[1] == 'factory_recover':
            data['iStatus'] = '0'
        else:
            return
        NetsWithinNets(data).entry()


if __name__ == '__main__':
    recover()
