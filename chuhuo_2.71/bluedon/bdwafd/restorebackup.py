import os

dbconfig = {
        "user": 'root'
        "passwd": 'bd_123456'
        }
obj_home = os.getcwd()

def restoretar():
    tar_files = []
    for dir_name in os.listdir(obj_home):
        extension_name = os.path.splitext(dir_name)[1]
        if extension_name and extension_name in '.tar':
            tar_files.append(dir_name)
    for tar_file in tar_files:
        os.system('tar xfP %s' % tar_file)

def restoresys():
    os.system('cp %s/sysctl.conf /etc/sysctl.conf' % obj_home)
    os.system('cp %s/crontab /etc/crontab' % obj_home)

def restoredb():
    os.system("mysql -u%s --password='%s' -e 'source %s/backup.sql'" % (dbconfig['user'], dbconfig['passwd'], obj_home))

if __name__ == "__main__":
    restoretar()
    #restoresys()
    #restoredb()
