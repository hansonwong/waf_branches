#!/usr/bin/python
#-*-encoding:UTF-8-*-
import logging
import sys
from lib.common import *

if __name__ == '__main__':
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    try:
        task_id = str(sys.argv[1])
        task_id = task_id.replace("#","")
        imgfile = "/var/webs/task%s.img" % (task_id)
        dir = "/var/webs/%s" % (imgfile.split("/")[-1].split(".")[0])
        filesize = 150
        
        type = sys.argv[2]
        if type == 'create':
            if create_dmfs(imgfile,filesize):
                print "create_dmfs success"
            else:
                logging.getLogger().error("create_dmfs failure, task_id:%s" % (task_id))
            #end if
        elif type == 'mount':
            if mount_dmfs(imgfile,dir):
                print "mount_dmfs success"
            else:
                logging.getLogger().error("mount_dmfs failure, task_id:%s" % (task_id))
            #end if
        elif type == 'umount':
            if umount_dmfs(imgfile,dir):
                print "umount_dmfs success"
            else:
                logging.getLogger().error("umount_dmfs failure, task_id:%s" % (task_id))
            #end if
        elif type == 'remove':
            if remove_dmfs(imgfile,dir):
                print "remove_dmfs success"
            else:
                logging.getLogger().error("remove_dmfs failure, task_id:%s" % (task_id))
            #end if
        else:
            logging.getLogger().error("UpdateMount.py argv error")
        #end if
        
    except Exception,e:
        logging.getLogger().error("File:UpdateMount.py, __main__:" + str(e))
    #end try
#end if

