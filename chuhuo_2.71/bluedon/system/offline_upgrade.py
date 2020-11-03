#! /usr/bin/env python
# -*- coding:utf-8 -*-


import os
import json


def tar_file(args):
    args = json.loads(args)
    for key in args:
        file_path = "/opt/lampp/htdocs/firewall/data/updatePackage/%s" % key
        cmd_use = {"IPS": "ips_update.sh",
                   "AV": "avdeff_update_offline",
                   "WAF": "waf_rulesupdate.sh"}
        python_path = os.getcwd()
    
        if not os.path.exists("/usr/local/rule_base/"):
            os.makedirs("/usr/local/rule_base/")

        cmd_path = "/usr/local/rule_base"
        file_name = args[key]
        tar_file_name = file_name.split(".tar.gz")[0]
        os.chdir(file_path)
        # 解密解压
        os.system("dd if=%s |openssl des3 -d -k 123456|tar zxf -" % file_name)
        os.system("mv %s %s" % (tar_file_name, cmd_path))
        os.system("rm -rf %s" % file_name)
        os.chdir(cmd_path)
        os.system("chmod 777 %s" % cmd_use[key])
        os.system("./%s %s/%s" % (cmd_use[key], cmd_path, tar_file_name))
        os.system("rm -rf %s" % tar_file_name)
        os.chdir(python_path)


# 加密压缩
def encrypt_rule():
    python_path = os.getcwd()
    data_name = "/usr/games/text/AV_rules_1.2.0.88"
    file_path = os.path.split(data_name)[0]
    file_name = os.path.split(data_name)[1]
    os.chdir(file_path)
    # k后面是密码
    os.system("tar -zcvf - %s |openssl des3 -salt -k 123456 | dd of=%s.tar.gz" % (file_name, file_name))
    # os.system("rm -rf %s" % file_name)
    os.chdir(python_path)


if __name__ == "__main__":
    # data = {"WAF": "WAF_rules_1.9.1.0.tar.gz"}
    encrypt_rule()
    # tar_file(data)


