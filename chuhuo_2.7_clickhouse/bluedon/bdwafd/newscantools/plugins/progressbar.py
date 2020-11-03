import os,sys,string   
import time   
import threading


def moveup(n):
    #print "\033[%dA" % n
    sys.stdout.flush()
#end def

class bar_unit(object):
    def __init__(self, name, now, total):
        self.now = now
        self.total = total
        self.name = name
    #end def
#end class


class ydy_progress(object):
    def __init__(self, bar_word, line_len):
    
        self.char = []
        
        self.char.append("\\")
        self.char.append("|")
        self.char.append("/")
        self.char.append("-")
        self.line_len = line_len
        
        #self.total = total
        self.bar_word = bar_word
        
        self.probar = []  #name:now|total
        
        self.mutex_probar = threading.Lock()
        
        self.lastlinenum = 0
    #end def
    
    def add(self, name, total):
        self.mutex_probar.acquire()
        self.probar.append(bar_unit(name, -1, int(total)))
        self.mutex_probar.release()
        
    
    def set_progress(self, name, now = -1):
        self.mutex_probar.acquire()
        
        
        for i in self.probar:
            if i.name == name:
                if now == -1:
                    i.now = i.now + 1
                else:
                    i.now = now
            #end if
        #end for
        
        tmplinenum = 0
        
        moveup(self.lastlinenum  + 1)
        
        
        for bar in self.probar:
            
            tmptotal = bar.total
            tmpnow   = bar.now
            tmpname  = bar.name
            tmpbarword = ""

            tmp = (float(tmpnow)*100)/float(tmptotal)
  
            for i in range(0, int(tmp * self.line_len/100)):   
  
                tmpbarword = tmpbarword + self.bar_word
            if tmpnow == tmptotal:
                iffinished = " -> finished"
            else:
                iffinished = ""
            print '\r[%s]\t%.2f%%\t%s:%s%s' % (tmpname, tmp, self.char[tmpnow % 4],tmpbarword, iffinished)
            #if tmpnow == tmptotal:
            #    os.write(1, " -> finished")
            
           # print "\n"
            
            tmplinenum = tmplinenum + 1
            self.lastlinenum = tmplinenum
            
            
        #end for
        
        
        
        self.mutex_probar.release()

if __name__ == '__main__':  
    import time
    
    mybar = ydy_progress("#", 30)
    
    mybar.add("name1", 123)
    mybar.add("name2", 123)
    mybar.add("name3", 123)
    mybar.add("name4", 123)
    mybar.add("name5", 123)
    
    #print "\n"
    for i in range(1, 124):
       
        mybar.set_progress("name1", i)
        mybar.set_progress("name2", i)
        mybar.set_progress("name3", i)
        mybar.set_progress("name4", i)
        mybar.set_progress("name5", i)
     
        time.sleep(0.1)
        
    
    
