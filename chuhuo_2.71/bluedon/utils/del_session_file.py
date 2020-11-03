#! /usr/bin/env python
# -*- coding:utf-8 -*-


import os
import json


def del_file_session(data):
    # print "PP:", data
    data = json.loads(data[0])
    results = data["sessionid"]
    # print "PPP:", results

    try:
        results = json.loads(results)
    except ValueError:
        pass

    for result in results:
        os.remove("/opt/lampp/temp/%s" % result)

    print "yes"
