#!/usr/bin/env python
# coding=utf-8


import os
import sys
import esm
import json

reload(sys)
sys.setdefaultencoding('utf-8')


SSLCONF = '/usr/local/bluedon/conf/ssl_config.json'

class SSLCategory(object):
    def __init__(self):
        super(SSLCategory, self).__init__()
        self.rules = dict()


    def load_ssl_conf(self):
        try:
            with open(SSLCONF, 'r') as fp:
                lines = fp.readlines()
            if len(lines) != 0: raw_conf = ''.join(lines)
            conf = json.loads(raw_conf)
        except:
            # log here
            return None

        return conf

    def update_rule(self):
        rules = self.load_ssl_conf()

        if rules is None:
            print 'None Rule in %s' % SSLCONF
            return

        # make esm
        for r in rules:
            if r.get('Host', None) is not None:
                finder = esm.Index()
                finder.enter(r.get('Host'))
                finder.fix()
                rule = r
                rule['Finder'] = finder
                self.rules[r.get('Host')] = rule
        print 'Updated SSL Rules'
        print self.rules

    def parse_line(self, msg):
        try:
            js = json.loads(msg)
        except ValueError:
            # log here
            print '%s is not a Valid JSON' % msg
            return ''

        site = js.get('ServerName', 'nothing_found_by_this_key')
        for rule_name, rule in self.rules.items():
            finder = rule.get('Finder')
            for (start, end), p in finder.query(site):
                # print 'found:[%s] in msg[%s]' % (p, msg)
                js['SiteName'] = rule['SiteName']
                js['Type'] = rule['Type']
                js['Host'] = site
                return json.dumps(js)

        return ''


if __name__ == '__main__':
    s = SSLCategory()
    s.load_ssl_conf()
    s.update_rule()
    line = "{\"AppProto\":\"SSL\",\"Date\":\"2017-2-20 16:20:37\",\"SrcMac\":\"f4-83-cd-96-81-07\",\"SrcIP\":\"192.168.2.101\",\"SrcPort\":\"51960\",\"DstMac\":\"30-b4-9e-18-d7-48\",\"DstIP\":\"140.205.174.93\",\"DstPort\":\"443\",\"ServerName\":\"ynuf.alipay.com\",\"NextProtocol\":\"http/1.1\"}"
    print s.parse_line(line)
    pass
