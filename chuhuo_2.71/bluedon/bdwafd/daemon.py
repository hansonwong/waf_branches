#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import sys, os, time, atexit, signal

exiting = 0

def sighandler(a,b):    
    global exiting
    exiting = 1
     
signal.signal(signal.SIGTERM,sighandler)   
 
class Daemon(object):
    """ A generic daemon class.
    
        Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null', debug=False):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.debug = debug
        
    def daemonize(self):
        """ do the UNIX double-fork magic, see Stevens' "Advanced
            Programming in the UNIX Environment" for details (ISBN 0201563177)
            http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
       
        # decouple from parent environment
        #os.chdir("/")
        os.setsid()
        os.umask(0)
       
        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
       
        # redirect standard file descriptors
        if not self.debug:
            sys.stdout.flush()
            sys.stderr.flush()
            si = file(self.stdin, 'r')
            so = file(self.stdout, 'a+')
            se = file(self.stderr, 'a+', 0)
            os.dup2(si.fileno(), sys.stdin.fileno())
            os.dup2(so.fileno(), sys.stdout.fileno())
            os.dup2(se.fileno(), sys.stderr.fileno())
        
        # write pidfile
        #atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """ Start the daemon """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
       
        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(0)
           
        # Start the daemon
        self.daemonize()

        # main loop
        self.begin()
        signal.signal(signal.SIGTERM,sighandler)   
        while True:
            global exiting
            if exiting:
                break
            time.sleep(1)
        self.end()
 
    def stop(self):
        """ Stop the daemon """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
       
        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart
 
        # Try killing the daemon process       
        try:
            while 1:
                os.kill(pid, signal.SIGKILL)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)
 
    def restart(self):
        """ Restart the daemon """
        self.stop()
        self.start()

    def begin(self):
        """ override in subclasses """
        pass

    def end(self):
        """ override in subclasses """
        pass

def main(daemon):
    import sys, argparse
    parser = argparse.ArgumentParser(description='A Daemon Application of Demo.')
    #parser.add_argument('-v', action='version', dest='version', version='0.51')
    #parser.add_argument("-p", action='store', dest='port')
    parser.add_argument('command', action='store', choices=['start', 'stop', 'restart'], help='action')
    args = parser.parse_args()
    app = Daemon('/tmp/daemon-server.pid')
    if args.command == 'start':
        app.start()
    elif args.command == 'stop':
        app.stop()
    elif args.command == 'restart':
        app.restart()
