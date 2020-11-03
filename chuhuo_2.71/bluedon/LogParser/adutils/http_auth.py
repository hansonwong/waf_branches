#!/usr/bin/env python
# coding=utf-8

import sys
import json
from ctypes import *
"""
    int bd_loginfo_unprotect(unsigned char *indata, int inlength,
                             unsigned char *outdata, int *outlength)

"""

res_null = {'pwd': '', 'user': ''}

def loginfo_unprotect(user, pw):
    res = res_null
    # load library
    so = cdll.LoadLibrary
    lib = so("/usr/lib/libsdktest.so")

    loginfo_unprotect = lib.bd_loginfo_unprotect
    loginfo_unprotect.argtypes = [POINTER(c_char), c_int, POINTER(c_char), POINTER(c_int)]

    # prepare parameter
    luser = len(user)
    user_data = create_string_buffer(256)
    luser_data = c_int(256)
    try:
        ret = loginfo_unprotect(user, luser, user_data, luser_data)
        if ret == 0:
            res['user'] = user_data.value
        else:
            # log here
            pass

        lpw = len(pw)
        pw_data = create_string_buffer(256)
        lpw_data = c_int(256)
        ret = loginfo_unprotect(pw, lpw, pw_data, lpw_data)
        if ret == 0:
            res['pwd'] = pw_data.value
        else:
            # log here
            pass
    except:
        res = res_null
        pass
    js = json.dumps(res)
    print js



if __name__ == '__main__':
    try:
        loginfo_unprotect(sys.argv[1], sys.argv[2])
    except Exception as e:
        # js = json.dumps(res_null)
        js = json.dumps({'pwd': '', 'user': ''})
        print js
