# coding:utf-8
import json
import sys
from db.mysql_db import select_one, select
from utils.log_logger import rLog_dbg
reload(sys)
sys.setdefaultencoding("utf-8")

ANTIVIRUS_PATH = '/etc/suricata/conf/antivirus.json'
DBG = lambda x: rLog_dbg('antivirus', x)


def antivirus_config():
    DBG('antivirus config start')
    sql = 'select sValue from m_tbconfig where sName="EvilProtectedSet"'
    data = json.loads(select_one(sql)['sValue'])
    # data['sFileType'] 为m_tbfiletypegroup中的id
    # data['sFileType'] == '1' 时，文件类型为所有,即所有文件类型的id是1
    if '1' in data['sFileType']:
        detect_type = 1
        file_type = ['']
    else:
        detect_type = 0
        # 文件类型组在对象定义中
        sql = 'select sFileExt from m_tbfiletypegroup where id in (%s)' \
            % ','.join(data['sFileType'])
        result = select(sql)
        file_type = []
        # 需要去掉*号以及去重处理
        for res in result:
            file_type.extend(res['sFileExt'].replace('*', '').lower().split(','))
        file_type = list(set(file_type))
        file_type = [{'type': i} for i in file_type]
    # iVirusType 为数组, 0为特征查杀(AvEngine), 1为机器学习(DeepEngine)
    template_args = {
        'AvEngine': int('0' in data['iVirusType']),     # 0,1 分别代表是否启用特征查杀
        'DeepEngine': int('1' in data['iVirusType']),   # 0,1 分别代表是否启用机器学习
        'ScanMode': int(data['iScanType']),             # 扫描模式
        'BpDetect': int(data.get('iFastScan', 0)),      # 是否启用断点续传
        'UncompressSize': int(data['iMaxDecompressionLever']),      # 最大解压层数
        'MaxFileSize': int(data['iMaxFileSize']),       # 最大文件大小
        'SetTime': int(data['iTime']) * 60,             # 阻断时间，永久为0
        'FileTypes': file_type,                         # 文件类型
        'AllType': detect_type,                         # 是否扫描所有文件类型
    }
    with open(ANTIVIRUS_PATH, 'w') as f:
        f.write(json.dumps(template_args, indent=2))
    DBG('antivirus config end')

if __name__ == '__main__':
    antivirus_config()
