#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, time, threading, shutil, subprocess
from logging import getLogger
from db import session_scope, Session, WafScanTask
from sqlalchemy import update

class ScanTask(threading.Thread):
    outputdir = '/var/wafDownload/loopholeScanResult/'
    
    def __init__(self):
        super(ScanTask,self).__init__(name = self.__class__.__name__)
        self.event = threading.Event()
        self.tasks = {'todo': [],
                      'doing': [],
                      'stop': []}
        self.skipfish = {}
        self.quit = 0

    def starttask(self, taskid):
        getLogger('main').info('scantask starttask %s' % (taskid,))
        self.tasks['todo'].append(taskid)

    def stoptask(self, taskid):
        if taskid not in self.tasks['doing']:
            getLogger('main').error('scantask taskid %s not found.' % (taskid,) )
        else:
            getLogger('main').info('scantask stoptask %s' % (taskid,))
            self.tasks['stop'].append(taskid)

    def deltask(self, taskid):
        getLogger('main').info('scantask deltask %s' % (taskid,))
        self.clearoutput(taskid)
    
    def deltaskskipfish(self, taskid):
        if self.skipfish.has_key(taskid):
            getLogger('main').info('scantask deltaskskipfish %s' % (taskid,))
            del self.skipfish[taskid]

    def clearoutput(self, taskid):
        getLogger('main').info('scantask clearoutput %s' % (taskid,))
        outputdir = self.outputdir + taskid
        if os.path.exists(outputdir) and os.path.isdir(outputdir):
            shutil.rmtree(outputdir)
        zipfile = outputdir+".zip"
        if os.path.exists(zipfile):
            os.remove(zipfile)

    def cleantask(self, taskid):
        files = ["child_index.js","index.html","issue_index.js","samples.js","summary.js"]
        targetdir = self.outputdir + taskid
        if os.path.exists(targetdir):
            for f in os.listdir(targetdir):
                if f in files:
                    continue
                tmpf = targetdir + "/" + f
                if os.path.isdir(tmpf):
                    shutil.rmtree(tmpf)
                elif os.path.isfile(tmpf):
                    os.remove(tmpf)
            zipstr = "zip %s.zip -r %s flaw" % (taskid, taskid)
            getLogger('main').info('command run: ' + zipstr)
            tmpproc = subprocess.Popen(zipstr.split(), cwd='/var/wafDownload/loopholeScanResult/')
            tmpproc.wait()

    def start(self):
        getLogger('main').debug(self.__class__.__name__+ ' starting...')
        super(ScanTask, self).start()
        getLogger('main').info(self.__class__.__name__+ ' started.')

    def stop(self):
        getLogger('main').debug(self.__class__.__name__+ ' Exiting...')
        self.event.set()
        self.join()
        getLogger('main').info(self.__class__.__name__+ ' Exited.')

    def proc(self):
        if self.event.isSet():
            self.quit = 1
            with session_scope() as session:
                if self.tasks['doing']:
                    for todo in self.tasks['doing']:
                        try:
                            self.skipfish[todo].kill()
                            self.skipfish[todo].wait()
                        except Exception, e:
                            pass
                        self.clearoutput(todo)
                        session.query(WafScanTask).filter(WafScanTask.id==int(todo)).update({WafScanTask.status: 3,})
                        self.deltaskskipfish(todo)
                for todo in self.tasks['todo']:
                    session.query(WafScanTask).filter(WafScanTask.id==todo).update({WafScanTask.status: 3,})
                for todo in self.tasks['stop']:
                    session.query(WafScanTask).filter(WafScanTask.id==todo).update({WafScanTask.status: 3,})
                return 0
        if self.tasks['doing']:
            for doingTaskid in self.tasks['doing']:
                poll = self.skipfish[doingTaskid].poll()
                if poll is not None:
                    if poll == 0:
                        getLogger('main').info('scantask %s Success.' % (doingTaskid,))
                        status = 2
                    else:
                        getLogger('main').info('scantask %s Fail, return %s.' % (doingTaskid, poll))
                        status = 4
                    with session_scope() as session:
                        session.query(WafScanTask).filter(WafScanTask.id==int(doingTaskid)).\
                            update({WafScanTask.status: status,
                                    WafScanTask.result: self.outputdir + doingTaskid,
                                    WafScanTask.endtime: int(time.mktime(time.localtime()))})
                    self.cleantask(doingTaskid)
                    self.tasks['doing'].remove(doingTaskid)
                    self.deltaskskipfish(doingTaskid)
                elif doingTaskid in self.tasks['stop']:
                    getLogger('main').info('scantask %s cancel.' % (doingTaskid,))
                    try:
                        self.skipfish[doingTaskid].kill()
                        self.skipfish[doingTaskid].wait()
                    except Exception, e:
                        pass
                    self.clearoutput(doingTaskid)
                    self.tasks['stop'].remove(doingTaskid)
                    self.tasks['doing'].remove(doingTaskid)
                    self.deltaskskipfish(doingTaskid)
        if self.tasks['todo']:
            taskid = self.tasks['todo'].pop(0)
            self.tasks['doing'].append(taskid)
            getLogger('main').info('scantask %s starting...' % (taskid,))
            with session_scope() as session:
                task = session.query(WafScanTask).filter(WafScanTask.id == int(taskid)).first()
                if not task:
                    getLogger('main').error('scantask %s todo, but not found in database' %(taskid,))
                else:
                    task.status = 1
                    self.clearoutput(taskid)
                    scanstr = "./skipfish -S dictionaries/complete.wl -W- -Y -o /var/wafDownload/loopholeScanResult/%s -k 01:00:00 -u %s" % (taskid, task.url)
                    getLogger('main').info('command run: ' + scanstr)
                    self.skipfish[taskid] = subprocess.Popen(scanstr.split(),
                                                     cwd='/usr/local/bluedon/bdwafd/scantools', 
                                                     stdout = subprocess.PIPE, 
                                                     stderr = subprocess.PIPE)
        if self.tasks['stop']:
            for todo in self.tasks['stop']:
                with session_scope() as session:
                    session.query(WafScanTask).filter(WafScanTask.id==todo).update({WafScanTask.status: 3,})
                self.clearoutput(self, todo)
                self.deltaskskipfish(todo)
            self.tasks['stop'] = []
        return 1

    def run(self):
        while True:
            try:
                if self.quit == 1:
                    return
                self.proc()
                time.sleep(1)
            except Exception, e:
                getLogger('main').exception(e)

if __name__ == '__main__':
    pass
