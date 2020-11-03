#!/usr/bin/python
#-*-encoding:UTF-8-*-
import sys
import logging
from lib.common import *

if __name__ == '__main__':
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    try:
        updateTaskManage()
        
    except Exception,e:
        logging.getLogger().error("File:UpdateTask.py, __main__:" + str(e))
    #end try
#end if

