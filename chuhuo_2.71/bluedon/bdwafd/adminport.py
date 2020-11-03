#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sysinfo_tables import WafSessionManager

if __name__ == '__main__':
    print '|'.join(WafSessionManager().GetNicNameByType('admin'))
