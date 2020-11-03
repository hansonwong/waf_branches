#!/usr/bin/env python
# coding=utf-8

import os
import sys
from safetydefend.IPS_builtin import insert_IPSrule
from db.mysql_db import update
from utils.log_logger import rLog_dbg, rLog_err

# debug function
# def DBG(x):
#     print x
#
# def ERR(x):
#     print x
LOGGER_NAME = 'ftp_auto_update'
DBG = lambda x : rLog_dbg(LOGGER_NAME, x)
ERR = lambda x : rLog_err(LOGGER_NAME, x)

class IpsRuleUpdate:
    def __init__(self,rule_path,version):
        self.rule_path=rule_path
        self.version=version

    def IPS_package_handle(self):
        """
        加压规则包,并将规则更新到目录'/etc/suricata/rules'
        """
        os.system('/usr/local/bdips/upgrade/update_rules.sh {rule_path}'.
                  format(rule_path=self.rule_path))

    def IPS_rules_table(self):
        """
        将目录规则/etc/suricata/rules/更新表格
        """
        insert_IPSrule()

    def update_version_info(self):
        update('update m_tbrolelib set sCurrentVersion="{version}" where sRelationLib="IPS"'.format(version=self.version))
        update('update m_tbsystem_info set IPSVersion="v{version}"'.format(version=self.version))

    def main(self):
        """

        """
        try:
            self.IPS_package_handle()
            self.IPS_rules_table()
            self.update_version_info()
        except Exception as e:
            ERR(e)


class AvRuleUpdate:
    def __init__(self, rule_path, version):
        self.rule_path = rule_path
        self.version = version
        self.tmp_path = '/tmp/av_update'

        if not os.path.exists(self.tmp_path):
            os.system('mkdir -p {}'.format(self.tmp_path))


    # uncompress
    def uncompress(self):
        os.system('dd if={p} |openssl des3 -d -k 123456|\
                  tar zxf - -C {t}'.format(p=self.rule_path, t=self.tmp_path))

        # rule_path is like AV_rules_x.x.x.x.tar.gz
        tar_name = os.path.split(self.rule_path)[-1]
        dir_name = tar_name.replace('.tar.gz', '')
        DBG(os.path.join(self.tmp_path, dir_name))
        return os.path.join(self.tmp_path, dir_name)

    def update(self, path):
        DBG('/home/cyren/src/avdeff_update_offline/avdeff_update_offline \
                  {p}'.format(p=path))
        os.system('/home/cyren/src/avdeff_update_offline/avdeff_update_offline \
                  {p}'.format(p=path))
        update('update m_tbsystem_info set VIRVersion="v{version}"'.format(version=self.version))
        update('update m_tbrolelib set sCurrentVersion="{version}" where sRelationLib="AV"'.format(version=self.version))

    def main(self):
        path = self.uncompress()
        self.update(path)

class WAFRuleUpdate:
    def __init__(self, rule_path, version):
        self.rule_path = rule_path
        self.version = version
        self.tmp_path = '/tmp/waf_update'
        self.update_script = 'updateRule.py'
        self.update_sql = 'updaterule.sql'

        if not os.path.exists(self.tmp_path):
            os.system('mkdir -p {}'.format(self.tmp_path))

    def uncompress(self):
        DBG("uncompress WAF")
        os.system('tar xzf {p} -C {t}'.format(p=self.rule_path, t=self.tmp_path))

        # rule_path is like WAF_rules_x.x.x.x.tar.gz
        tar_name = os.path.split(self.rule_path)[-1]
        dir_name = tar_name.replace('.tar.gz', '')
        DBG(os.path.join(self.tmp_path, dir_name))
        return os.path.join(self.tmp_path, dir_name)
        pass

    def update(self, update_script_path):
        DBG("updating WAF")
        full_update_script = os.path.join(update_script_path, self.update_script)
        full_update_sql = os.path.join(update_script_path, self.update_sql)
        DBG('python {p} {arg}'.format(p=full_update_script, arg=full_update_sql))
        os.system('python {p} {arg}'.format(p=full_update_script, arg=full_update_sql))
        update('update m_tbsystem_info set WAFVersion="v{version}"'.format(version=self.version))
        update('update m_tbrolelib set sCurrentVersion="{version}" where sRelationLib="WAF"'.format(version=self.version))
        pass

    def main(self):
        path = self.uncompress()
        self.update(path)
        pass

if __name__=='__main__':
    # IPS
    # cls=IpsRuleUpdate('/usr/local/bdips/upgrade/output/IPS_rules_1.0.0.4.tar.gz','1.0.0.4')
    # cls.main()

    # AV
    # cls = AvRuleUpdate('/tmp/AV_rules_1.0.0.4.tar.gz', '1.0.0.4')
    # cls.main()

    # WAF
    cls = WAFRuleUpdate('/tmp/ftp_down/WAF_rules_1.0.0.4.tar.gz', '1.0.0.4')
    cls.main()
