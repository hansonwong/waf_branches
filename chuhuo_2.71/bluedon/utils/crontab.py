import os

from utils.log_logger import FWLOG_DEBUG


PATH = '/etc/cron.d/bd_log_cron'
#PATH = './crontab'

def add_crontab(mark,cmd):
    if if_exist(mark) == False:
        with open(PATH,'a+') as fp:
            fp.write('#%s\n' % mark)
            fp.write('%s\n' % cmd)
        return

def update_crontab(mark,cmd):
    if if_exist(mark):
        FWLOG_DEBUG('modify crontab [%s] [%s]' % (mark, cmd))
        with open(PATH,'r') as fp:
            lst = fp.readlines()
            #print 'before:',lst
        smark = '#%s\n' % mark
        #if smark in lst:
        lst[lst.index(smark) + 1] = cmd.strip('\n') + '\n'
        with open(PATH,'w') as fp:
            fp.write(('').join(lst))
    else:
        add_crontab(mark,cmd)
        FWLOG_DEBUG('add crontab [%s] [%s]' % (mark, cmd))
    return

def if_exist(mark):
    with open(PATH,'r') as fp:
        lines = fp.readlines()

    l = '#%s\n' % mark
    return True if l in lines else False



def delete_crontab(mark):
    if if_exist(mark):
        with open(PATH,'r') as fp:
            lst = fp.readlines()
            #print 'before:',lst
        smark = '#%s\n' % mark
        if smark in lst:
            lst.pop(lst.index(smark) + 1)
            lst.pop(lst.index(smark))
        with open(PATH,'w') as fp:
            fp.write(('').join(lst))

    return

if __name__ == '__main__':
    #add_crontab('test1','*/1 * * * * root echo "bbb" >> /root/Desktop/1.txt')
    #add_crontab('test','*/1 * * * * root echo "bbb" >> /root/Desktop/1.txt')
    #update_crontab('test','*/1 * * * * root echo "acc" >> /root/Desktop/1.txt')
    #delete_crontab('test1')
    pass
