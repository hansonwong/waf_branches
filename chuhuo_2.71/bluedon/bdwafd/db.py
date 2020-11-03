# -*- coding: utf-8 -*-
from contextlib import contextmanager
import os
import datetime
import re
import sqlalchemy
from sqlalchemy import (
    Column, Integer, String, SmallInteger, BigInteger,
    Index, DateTime, Float, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import PrimaryKeyConstraint
from MySQLdb import escape_string
import MySQLdb
from config import config

Base = declarative_base()
constr = "mysql://%s:%s@%s/%s?charset=utf8&unix_socket=%s" % (
config['db']['user'], config['db']['passwd'], config['db']['host'], config['db']['db'], config['db']['unix_socket'])
engine = create_engine(constr, encoding='utf-8')
Session = sessionmaker(bind=engine)

fw_constr = "mysql://%s:%s@%s/%s?charset=utf8&unix_socket=%s" % (
config['dbfw']['user'], config['dbfw']['passwd'], config['dbfw']['host'], config['dbfw']['db'],
config['dbfw']['unix_socket'])
fw_engine = create_engine(fw_constr, encoding='utf-8')

logs_constr = "mysql://%s:%s@%s/%s?charset=utf8&unix_socket=%s" % (
config['dbacc']['user'], config['dbacc']['passwd'], config['dbacc']['host'], config['dbacc']['db'],
config['dbacc']['unix_socket'])
logs_engine = create_engine(logs_constr, encoding='utf-8')


class DictToOb(object):
    def __init__(self, map):
        self.map = map

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)

    def __getattr__(self, name):
        v = self.map[name]
        if isinstance(v, (dict)):
            return DictToOb(v)
        if isinstance(v, (list)):
            r = []
            for i in v:
                r.append(DictToOb(i))
            return r
        else:
            return self.map[name];

    def __getitem__(self, name):
        return self.map[name]


def row2dict(row):
    if not row:
        return {}
    d = {}
    for column in row.__table__.columns:
        d[column.name] = getattr(row, column.name)
    return d


def rows2list(rows):
    l = []
    for row in rows:
        d = {}
        for column in row.__table__.columns:
            d[column.name] = getattr(row, column.name)
        l.append(d)
    return l


def formatcksqlstr(datas):
    tmp_data = []
    for data in datas:
        if data:
            if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:', data):
                data = datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
            else:
                data = str(data)
                data = data.encode('string-escape')
        else:
            data = 'none'
        tmp_data.append(data)
    return tuple(tmp_data)


def formatsqlstr(datas):
    tmp_data = []
    for data in datas:
        if data:
            data = str(data)
            data = data.encode('string-escape')
        tmp_data.append(data)
    return tuple(tmp_data)


@contextmanager
def session_scope(bind=engine):
    session = Session(bind=bind)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def fw_session_scope():
    session = Session(bind=fw_engine)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def conn_scope(*args, **kwargs):
    conn = MySQLdb.connect(*args, **kwargs)
    cursor = conn.cursor()
    try:
        yield conn, cursor
        conn.commit()
    finally:
        cursor.close()
        conn.close()


class OverFlowSet(Base):
    __tablename__ = 't_overflowset'

    id = Column(Integer)
    name = Column(String, primary_key=True)
    value = Column(Integer)
    status = Column(Integer)
    secname = Column(String)

    def __repr__(self):
        return "<OverFlowSet(id='%s', name='%s', value='%s', status='%s')>" % (
        self.id, self.name, self.value, self.status)


class HttpTypeSet(Base):
    __tablename__ = "t_httptypeset"

    id = Column(Integer, primary_key=True)
    name = Column(String(45))
    desc = Column(String(45))
    selected = Column(Integer)

    def __repr__(self):
        return "<t_httptypeset(id='%s',name='%s')>" % (self.id, self.name)


class Rules(Base):
    __tablename__ = "t_rules"

    id = Column(Integer, primary_key=True)
    realid = Column(Integer)
    name = Column(String(255))
    content = Column(String(1024))
    desc = Column(String(1024))
    type = Column(String(45))
    action = Column(String(45))
    status = Column(Integer)
    update_time = Column(Integer)
    redirect_id = Column(Integer)

    def __repr__(self):
        return "<t_Rules(id='%s',realid='%s',name='%s')>" % (self.id, self.realid, self.name)


class ReverseProxy(Base):
    __tablename__ = 't_reverporxy'

    id = Column(Integer, primary_key=True)
    host = Column(String)
    proto = Column(String)
    hatype = Column(String)
    cache = Column(Integer)
    helthcheck = Column(Integer)
    locals = Column(String)
    servers = Column(String)
    remark = Column(String(1024))

    def __repr__(self):
        return "<ReverseProxy(host='%s', locals='%s', servers='%s')>" % (self.host, self.locals, self.servers)


class Dns(Base):
    __tablename__ = 't_dns'

    first = Column(String, primary_key=True)
    second = Column(String)

    def __repr__(self):
        return "<Dns(first='%s', second='%s')>" % (self.first, self.second)


# class Ocr(Base):
#     __tablename__ = 't_ocr_block'
#
#     id = Column(Integer, primary_key=True)
#     status = Column(Integer)
#     urls = Column(String)
#     exts = Column(String)
#     words = Column(String)
#     website_id = Column(Integer)
#     update_time = Column(Integer)
#
#     def __repr__(self):
#         return "<Ocr(status='%d', urls='%s', exts='%s', words='%s', website_id='%d', update_time='%d')>" % (self.status, self.urls, self.exts, self.words, self.website_id, self.update_time)


class ConfigField(Base):
    __tablename__ = 'config'

    symbol = Column(String, primary_key=True)
    desc = Column(String)
    field_desc = Column(String)
    json = Column(String)

    def __repr__(self):
        return "<Config(symbol='%s', desc='%s', field_desc='%s', json='%s')>" % (
        self.symbol, self.desc, self.field_desc, self.json)


def data_type_match(symbol):
    if symbol == "BaseConfig":
        type_list = {"wafEngine": "str", "defaultAction": "str", "ports": "str", "deploy": "str",
                     "blackAndWhite": "str"}

    elif symbol == "ByPass":
        type_list = {"enable": "int"}

    elif symbol == "CcSet":
        type_list = {"ccEnable": "int", "ccPeriod": "int", "ccTimes": "int", "ccBlockTime": "int",
                     "brouteEnable": "int", \
                     "broutePeriod": "int", "brouteTimes": "int", "brouteUris": "str", "brouteBlockTime": "int"}

    elif symbol == "DDosSet":
        type_list = {"bankWidth": "int", "totalPacket": "int", "perPacket": "int", "tcpPacket": "int",
                     "perTcpPacket": "int", \
                     "synPacket": "int", "perSynPacket": "int", "ackPacket": "int", "perAckPacket": "int",
                     "otherTcp": "int", \
                     "perOtherTcp": "int", "udpPacket": "int", "perUdpPacket": "int", "icmpPacket": "int",
                     "perIcmpPacket": "int", \
                     "ddosEnable": "int", "udpEnable": "int", "icmpEnable": "int"}

    elif symbol == "DiskClear":
        type_list = {"enable": "int", "limit": "int"}

    elif symbol == "FileExtension":
        type_list = {"extension": "list", "extensionHidden": "int"}

    elif symbol == "HostLinkProtection":
        type_list = {"fileType": "list"}

    elif symbol == "IntelligentTrojanHorseSet":
        type_list = {"status": "int", "interceptedFileSuffix": "list", "maxFileSize": "int", "updateTime": "int"}

    elif symbol == "IpFilterSet":
        type_list = {"enable": "int", "ip": "list"}

    elif symbol == "KeyWordAlert":
        type_list = {"maxFileSize": "int", "urls": "list", "exts": "list", "words": "list", "alertConfig": "str",
                     "status": "int", "isBlock": "int"}

    elif symbol == "MailAlert":
        type_list = {"status": "int", "interval": "int", "now": "int", "phoneStatus": "int", "maxValue": "int",
                     "cycle": "int", "phoneCycle": "int"}

    elif symbol == "MailSet":
        type_list = {"openMail": "int", "openPhone": "int", "smtpPort": "int", "sender": "str", "userName": "str",
                     "password": "str", \
                     "smtpServer": "str", "receiver": "str", "receiverPhone": "str"}

    elif symbol == "OcrSet":
        type_list = {"status": "int", "websiteId": "int", "words": "list", "updateTime": "str", "urls": "list",
                     "exts": "list"}

    elif symbol == "OutLinkSet":
        type_list = {"enable": "int", "dports": "str"}

    elif symbol == "SelfStudyResult":
        type_list = {"uriMax": "int", "argNameMax": "int", "argContentMax": "int", "argCountMax": "int",
                     "cookieMax": "int", "cookieNameMax": "int", "cookieContentMax": "int", "cookieCountMax": "int"}

    elif symbol == "SelfStudySet":
        type_list = {"isIpBlack": "int", "isDomainblack": "int", "isUse": "int", "isIpWhite": "int",
                     "isUseResult": "int"}

    elif symbol == "SensitiveWord":
        type_list = {"enable": "int", "words": "list"}

    elif symbol == "ServerHeaderHide":
        type_list = {"list": "str"}

    elif symbol == "SmartBlock":
        type_list = {"enable": "int", "cycle": "int", "invadeCount": "int", "standardBlockTime": "int"}

    elif symbol == "SpiderDefend":
        type_list = {"list": "list"}

    elif symbol == "WafSsh":
        type_list = {"enable": "int"}

    return type_list


def data_type_change(symbol, result):
    type_list = data_type_match(symbol)
    for param, type in type_list.items():
        if type == "int":
            result[param] = int(result[param]) if result[param] else ""
        elif type == "str":
            result[param] = str(result[param]) if result[param] else ""
        elif type == "list":
            result[param] = result[param] if result[param] else []
    return result


def get_config(symbol):
    with session_scope() as session:
        conf = session.query(ConfigField).filter(ConfigField.symbol == '%s' % symbol).first()
        json = conf.json
        result = eval(json)
    result = data_type_change(symbol, result)
    return result

def replace_null_value(rows):
    result = []
    for row in rows:
        row = row2dict(row)
        for key,value in row.items():
            if value is None:
                row[key] = ""
        row = DictToOb(row)
        result.append(row)
    return result

class License(Base):
    __tablename__ = "t_license"

    sn = Column(String(100), primary_key=True)
    vertype = Column(SmallInteger)
    validate = Column(Integer)
    company = Column(String(100))
    address = Column(String(255))
    email = Column(String(45))
    telephone = Column(String(100))
    licensefile = Column(String(255))

    def __repr__(self):
        return "<t_license(sn='%s',vertype='%d',validate='%d',licensefile='%s')>" % (
        self.sn, self.vertype, self.validate, self.licensefile)


class WafSysInfo(Base):
    __tablename__ = "t_sysinfo"

    id = Column(Integer, primary_key=True)
    time = Column(Integer)
    cpu_ratio = Column(Integer)
    total_mem = Column(Integer)
    used_mem = Column(Integer)
    total_disk = Column(Integer)
    used_disk = Column(Integer)

    def __repr__(self):
        return "<t_sysinfo(time='%d',cpu_ratio='%d',total_mem='%d',used_mem='%d',total_disk='%d',used_disk='%d')>" % \
               (self.time, self.cpu_ratio, self.total_mem, self.used_mem, self.total_disk, self.used_disk)


class WafNetflowHistory(Base):
    __tablename__ = "t_netflowhistory"

    nic = Column(String(20))
    time = Column(Integer)
    flowin = Column(BigInteger)
    flowout = Column(BigInteger)
    __table_args__ = (
        PrimaryKeyConstraint('nic', 'time'),
        {},
    )

    def __repr__(self):
        return "<t_netflowhistory(nic='%s',time='%d',flowin='%d',flowout='%d')>" % (
        self.nic, self.time, self.flowin, self.flowout)


class WafNicsFlow(Base):
    __tablename__ = "t_nicsflow"

    nic = Column(String(10), primary_key=True)
    mac = Column(String(45))
    mode = Column(String(4))
    status = Column(SmallInteger)  # link status
    rcv_pks = Column(BigInteger)
    snd_pks = Column(BigInteger)
    rcv_bytes = Column(BigInteger)
    snd_bytes = Column(BigInteger)
    rcv_errs = Column(Integer)
    snd_errs = Column(Integer)
    rcv_losts = Column(Integer)
    snd_losts = Column(Integer)
    rcv_ratio = Column(Integer)
    snd_ratio = Column(Integer)
    time = Column(Integer)

    def __repr__(self):
        return "<t_nicsflow(nic='%s',status='%d',rcv_ratio='%d',snd_ratio='%d')>" % \
               (self.nic, self.status, self.rcv_ratio, self.snd_ratio)


class WafNicSet(Base):
    __tablename__ = "t_nicset"

    nic = Column(String(45), primary_key=True)
    lan_port = Column(String(20))
    lan_type = Column(String(20))
    mac = Column(String(20))
    ip = Column(String(45))
    mask = Column(String(45))
    gateway = Column(String(45))
    isstart = Column(SmallInteger)
    islink = Column(SmallInteger)
    workmode = Column(String(45))
    desc = Column(String(45))
    brgname = Column(String(45))
    workpattern = Column(String(45))

    def __repr__(self):
        return "<t_nicsflow(lan_port='%s', lan_type='%s', mac='%s',nic='%s',ip='%s',mask='%s',gateway='%s',\
        isstart='%d',islink='%d',workmode='%s',desc='%s',brgname='%s')>" % \
               (self.lan_port, self.lan_type, self.mac, self.nic, self.ip, self.mask, self.gateway, \
                self.isstart, self.islink, self.workmode, self.desc, self.brgname)


Index('fk_t_nicset_t_bridges1_idx', WafNicSet.brgname.asc())


class WafBridge(Base):
    __tablename__ = "t_bridge"
    name = Column(String(45), primary_key=True)
    nics = Column(String(256))  # for many vlan
    ageingtime = Column(Integer)
    stp = Column(SmallInteger)
    forwarddelay = Column(Integer)
    maxage = Column(Integer)
    hellotime = Column(Integer)
    level = Column(Integer)

    def __repr__(self):
        return "<t_bridge(name='%s',nics='%s',agingtime='%d',stp='%d',\
		fwddelay='%d',maxage='%d',hellotime='%d',level='%d'" % \
               (self.name, self.nics, self.ageingtime, self.stp, self.forwarddelay, self.maxage, self.hellotime,
                self.level)


class WafRoute(Base):
    __tablename__ = "t_staticroute"
    nic = Column(String(45), primary_key=True)
    isdefault = Column(SmallInteger, primary_key=True)
    dest = Column(String(45), primary_key=True)
    mask = Column(String(45), primary_key=True)
    gateway = Column(String(45), primary_key=True)

    def __repr__(self):
        return "<t_staticroute(nic='%s',dest='%s',mask='%s',gateway='%s'" % \
               (self.nic, self.dest, self.mask, self.gateway)


class WafScanTask(Base):
    __tablename__ = "t_scantask"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    url = Column(String(255))
    starttime = Column(Integer)
    endtime = Column(Integer)
    status = Column(SmallInteger)
    result = Column(String(255))  # path to the scanned result

    def __repr__(self):
        return "<t_scantask(name='%s',url='%s',status='%d',result='%s'" % \
               (self.name, self.url, self.status, self.result)


class Pcap(Base):
    __tablename__ = 't_pcap'
    id = Column(Integer, primary_key=True)
    net = Column(String(50))
    port = Column(String(50))
    token = Column(String(200))
    path = Column(String(255))
    time = Column(String(50))
    userid = Column(Integer)
    pid = Column(Integer)
    status = Column(Integer)
    createtime = Column(Integer)
    updatetime = Column(Integer)

    def __repr__(self):
        return "<t_pcap(id='%d', net='%s', port='%s', token='%s', path='%s', userid='%d', pid='%d')>" % \
               (self.id, self.net, self.port, self.token, self.path, self.userid, self.pid)


class ErrorList(Base):
    __tablename__ = "t_errorlist"
    id = Column(Integer, primary_key=True)
    status_code = Column(String(20))
    prompt_type = Column(Integer)
    prompt_file = Column(String(100))
    prompt_content = Column(String(255))
    desc = Column(String(255))
    status = Column(Integer)

    def __repr__(self):
        return "<t_errorlist(status_code='%s',prompt_type='%d',prompt_file='%s',prompt_content='%s',status='%d'" % \
               (self.status_code, self.prompt_type, self.prompt_file, self.prompt_content, self.status)


class AlertReport(Base):
    __tablename__ = "t_alertreport"

    id = Column(Integer, primary_key=True)
    LogDateTime = Column(DateTime)
    Url = Column(String(512))
    Host = Column(String(255))
    TypeName = Column(String(45))
    SourceIP = Column(String(15))

    def retvalues(self):
        values = "('%s', '%s', '%s', '%s', '%s')," % (
        self.LogDateTime, self.Url, self.Host, self.TypeName, self.SourceIP)
        return values


class AlertLogSet(Base):
    __tablename__ = "t_alertlogs"

    id = Column(Integer, primary_key=True)
    AuditLogUniqueID = Column(String(24))
    LogDateTime = Column(DateTime)
    CountryCode = Column(String(3), default='CN')
    RegionCode = Column(String(8), default='unknown')
    City = Column(String(32), default='unknown')
    SourceIP = Column(String(15))
    SourcePort = Column(String(8))
    DestinationIP = Column(String(15))
    DestinationPort = Column(String(8))
    Referer = Column(String(255))
    UserAgent = Column(String(255))
    HttpMethod = Column(String(8))
    Url = Column(String(512))
    HttpProtocol = Column(String(16))
    Host = Column(String(255))
    RequestContentType = Column(String(255))
    ResponseContentType = Column(String(255))
    HttpStatusCode = Column(String(4))
    GeneralMsg = Column(String(512))
    Rulefile = Column(String(255))
    RuleID = Column(String(10))
    MatchData = Column(String(255))
    Rev = Column(String(128))
    Msg = Column(String(128))
    Severity = Column(String(16))
    Tag = Column(String(64))
    Status = Column(String(8))
    LogSource = Column(String(8))
    AttackType = Column(String(128))
    Uri = Column(String(512))
    QueryString = Column(String(512))

    def sqlact(self):
        ccsql = """insert into t_cclogs(AuditLogUniqueID, LogDateTime, CountryCode, RegionCode, City,
                    SourceIP, SourcePort, DestinationIP, DestinationPort, Referer, UserAgent, HttpMethod,
                    Url, HttpProtocol, Host, RequestContentType, ResponseContentType, HttpStatusCode,
                    GeneralMsg, Rulefile, RuleID, MatchData, Rev, Msg, Severity, Tag, Status, LogSource, 
                    AttackType, Uri, QueryString) values"""
        alertsql = """insert into t_alertlogs(AuditLogUniqueID, LogDateTime, CountryCode, RegionCode, City, SourceIP, SourcePort, DestinationIP, DestinationPort, Referer, UserAgent, HttpMethod, Url, HttpProtocol, Host, RequestContentType, ResponseContentType, HttpStatusCode, GeneralMsg, Rulefile, RuleID, MatchData, Rev, Msg, Severity, Tag, Status, LogSource, AttackType, Uri, QueryString) values"""
        alertreportsql = "insert into t_alertreport(LogDateTime, Url, Host, TypeName, SourceIP) values"

        dictsql = {'EMERGENCY': 0, 'ALERT': 0, 'CRITICAL': 0, 'ERROR': 0, 'WARNING': 0, 'NOTICE': 0, 'INFO': 0,
                   'DEBUG': 0}
        return [ccsql, alertsql, dictsql, {}, [], [], [], alertreportsql]

    def getvalues(self):
        return formatcksqlstr((self.AuditLogUniqueID, self.LogDateTime, self.CountryCode, self.RegionCode, self.City,
                               self.SourceIP, self.SourcePort, self.DestinationIP, self.DestinationPort, self.Referer,
                               self.UserAgent, self.HttpMethod, self.Url, self.HttpProtocol, self.Host,
                               self.RequestContentType, self.ResponseContentType, self.HttpStatusCode, self.GeneralMsg,
                               self.Rulefile, self.RuleID, self.MatchData, self.Rev, self.Msg, self.Severity, self.Tag,
                               self.Status, self.LogSource, self.AttackType, self.Uri, self.QueryString))

    def retvalues(self):
        values = """('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',
                  '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s',
                  '%s', '%s'),""" % \
                 formatsqlstr((self.AuditLogUniqueID, self.LogDateTime, self.CountryCode, self.RegionCode, self.City,
                               self.SourceIP, self.SourcePort, self.DestinationIP, self.DestinationPort, self.Referer,
                               self.UserAgent, self.HttpMethod, self.Url, self.HttpProtocol, self.Host,
                               self.RequestContentType,
                               self.ResponseContentType, self.HttpStatusCode, self.GeneralMsg, self.Rulefile,
                               self.RuleID,
                               self.MatchData, self.Rev, self.Msg, self.Severity, self.Tag, self.Status, self.LogSource,
                               self.AttackType, self.Uri, self.QueryString))
        # (self.AuditLogUniqueID, self.LogDateTime, self.CountryCode, self.RegionCode, self.City,
        # self.SourceIP,self.SourcePort, self.DestinationIP, self.DestinationPort, self.Referer,
        # self.UserAgent,self.HttpMethod,self.Url,self.HttpProtocol,self.Host,self.RequestContentType,
        # self.ResponseContentType, self.HttpStatusCode, self.GeneralMsg, self.Rulefile, self.RuleID,
        # self.MatchData, self.Rev, self.Msg, self.Severity, self.Tag, self.Status, self.LogSource,
        # self.AttackType, self.Uri, self.QueryString)

        # values = str(tuple(map(lambda x: '{}'.format(x), (self.AuditLogUniqueID, self.LogDateTime,
        # self.CountryCode, self.RegionCode, self.City,
        # self.SourceIP,self.SourcePort, self.DestinationIP, self.DestinationPort, self.Referer,
        # self.UserAgent,self.HttpMethod,self.Url,self.HttpProtocol,self.Host,self.RequestContentType,
        # self.ResponseContentType, self.HttpStatusCode, self.GeneralMsg, self.Rulefile, self.RuleID,
        # self.MatchData, self.Rev, self.Msg, self.Severity, self.Tag, self.Status, self.LogSource,
        # self.AttackType, self.Uri, self.QueryString))))

        # values = "(" + "'" + self.AuditLogUniqueID + "'" + ","
        # # os.system('echo "%s __%s" >> /tmp/sql' %(self.AuditLogUniqueID, self.UserAgent))
        # values = values + "'" + self.LogDateTime + "'" + ","
        # values = values + "'" + self.CountryCode + "'" + ","
        # # values = values + "'" + self.RegionCode + "'" + ","
        # values = "%s '%s'," % (values, self.RegionCode)
        # # values = values + "'" + self.City + "'" + ","
        # values = "%s '%s'," % (values, self.City)
        # values = values + "'" + self.SourceIP + "'" + ","
        # values = values + "'" + self.SourcePort + "'" + ","
        # values = values + "'" + self.DestinationIP + "'" + ","
        # values = values + "'" + self.DestinationPort + "'" + ","
        # values = values + "'" + self.Referer + "'" + ","
        # values = values + "'" + unicode(self.UserAgent, 'utf-8') + "'" + ","
        # values = values + "'" + self.HttpMethod + "'" + ","
        # values = values + "'" + unicode(self.Url, 'utf-8') + "'" + ","
        # values = values + "'" + self.HttpProtocol + "'" + ","
        # values = values + "'" + self.Host + "'" + ","
        # # values = values + "'" + self.RequestContentType + "'" + ","
        # values = "%s '%s'," % (values, self.RequestContentType)
        # values = values + "'" + self.ResponseContentType + "'" + ","
        # # values = values + "'" + self.HttpStatusCode + "'" + ","
        # values = "%s '%s'," % (values, self.HttpStatusCode)
        # values = values + "'" + self.GeneralMsg + "'" + ","
        # values = values + "'" + self.Rulefile + "'" + ","
        # values = values + "'" + self.RuleID + "'" + ","
        # values = values + "'" + self.MatchData + "'" + ","
        # values = values + "'" + self.Rev + "'" + ","
        # values = values + "'" + self.Msg + "'" + ","
        # values = values + "'" + self.Severity + "'" + ","
        # values = values + "'" + self.Tag + "'" + ","
        # values = values + "'" + self.Status + "'" + "),"

        # os.system('echo "%s" >> /tmp/sql' % (values))
        return values


class WafLogSet(Base):
    __tablename__ = "t_waflogs"

    id = Column(Integer, primary_key=True)
    src_ip = Column(String(30))
    url = Column(String(45))
    location = Column(String(45))
    desc = Column(String(1024))
    rules_id = Column(Integer, default=0)
    time = Column(Integer)

    def __repr__(self):
        return "<t_alertlogs(id='%s', src_ip='%s')>" % (self.id, self.src_ip)


class LogFileSet(Base):
    __bind_key__ = 'logs'
    __tablename__ = "t_fileseat"

    id = Column(Integer, primary_key=True)
    StdDir = Column(String(50))
    Sdate = Column(String(8))
    Stime = Column(String(13))

    def __repr__(self):
        return "<t_fileseat(StdDir='%s',Sdate='%s',Stime='%s')>" % (self.StdDir, self.Sdate, self.Stime)


class BaseAccessCtrl(Base):
    __tablename__ = "t_baseaccessctrl"

    id = Column(Integer, primary_key=True)
    action = Column(String(20), default='block')
    status = Column(Integer)
    desc = Column(String(255))
    src_ips = Column(String(100))
    dest_ips = Column(String(100))
    url = Column(String(1024))
    realid = Column(Integer)
    type = Column(String(100))

    def __repr__(self):
        return "<t_baseaccessctrl(id='%s')>" % (self.id)


class HttpRequestType(Base):
    __tablename__ = "t_httprequesttype"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    status = Column(Integer())

    def __repr__(self):
        return "<t_httprequesttype(id='%s')>" % (self.id)


class HttpVer(Base):
    __tablename__ = "t_httpver"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    status = Column(Integer())

    def __repr__(self):
        return "<t_httpver(id='%s')>" % (self.id)


# class RestrictExt(Base):
#     __tablename__ = "t_restrictext"
#
#     id             = Column(Integer,primary_key=True)
#     name           = Column(String())
#     status         = Column(Integer())
#
#     def __repr__(self):
#         return "<t_restrictext(id='%s')>" % (self.id)

class RestrictHeaders(Base):
    __tablename__ = "t_restrictheaders"

    id = Column(Integer, primary_key=True)
    name = Column(String())
    status = Column(Integer())

    def __repr__(self):
        return "<t_restrictheaders(id='%s')>" % (self.id)


# class BaseConfig(Base):
#     __tablename__ = "t_baseconfig"
#
#     wafengine       = Column(String(),primary_key=True)
#     defaultaction   = Column(String())
#     ports           = Column(String())
#     deploy          = Column(String())
#
#     def __repr__(self):
#         return "<t_baseconfig(id='%s')>" % (self.wafengine)

# class MailSet(Base):
#     __tablename__ = "t_mailset"
#
#     sender         = Column(String(),primary_key=True)
#     username       = Column(String())
#     password       = Column(String())
#     smtpserver     = Column(String())
#     smtp_port      = Column(String())
#     receiver       = Column(String())
#     receiver_phone = Column(String())
#
#     def __repr__(self):
#         return "<t_mailset(sender='%s')>" % (self.sender)

# class MailAlert(Base):
#     __tablename__ = "t_mailalert"
#
#     status       = Column(Integer(),primary_key=True)
#     now          = Column(Integer())
#     interval     = Column(Integer())
#     maxValue     = Column(Integer())
#     cycle        = Column(String())
#     phone_status = Column(Integer())
#     phone_cycle  = Column(String())
#
#     def __repr__(self):
#         return "<t_mailalert(status='%s')>" % (self.status)

class RuleSet(Base):
    __tablename__ = "t_ruleset"

    id = Column(Integer, primary_key=True)
    modelname = Column(String(20), primary_key=True)
    selectedfiles = Column(String(1024))
    ischecked = Column(SmallInteger())
    isdefault = Column(SmallInteger())

    def __repr__(self):
        return "<t_ruleset(modename='%s',selectedfiles='%s')>" % (self.modename, self.selectedfiles)


class RuleFiles(Base):
    __tablename__ = "t_rulefiles"

    id = Column(Integer(), primary_key=True)
    filename = Column(String(255))
    ruleids = Column(String(2048))
    desc = Column(String(1024))
    type = Column(String(45))

    def __repr__(self):
        return "<t_rulefiles(filename='%s',ruleids='%s',desc='%s')>" % (self.filename, self.ruleids, self.desc)


class AdvAccessCtrl(Base):
    __tablename__ = "t_advaccessctrl"

    id = Column(Integer(), primary_key=True)
    status = Column(Integer())
    desc = Column(String(255))
    src_ips = Column(String(100))
    dest_ips = Column(String(100))
    url = Column(String(1024))
    action = Column(String(45))

    def __repr__(self):
        return "<t_advaccessctrl(id='%s')>" % (self.id,)


class CustomRules(Base):
    __tablename__ = "t_customrules"

    realid = Column(Integer(), primary_key=True)
    priority = Column(Integer())
    name = Column(String())
    desc = Column(String())
    severity = Column(String())
    action = Column(String())
    status = Column(String())
    httpdata = Column(String())
    httptype = Column(String())
    matchdata = Column(String())
    matchalgorithm = Column(Integer())
    keywords = Column(String())

    def __repr__(self):
        return "<t_customrules(realid='%s')>" % (self.realid,)


# class CCSet(Base):
#     __tablename__ = "t_ccset"
#
#     id              = Column(Integer(),primary_key=True)
#     ccswitch        = Column(Integer())
#     ccperiod        = Column(Integer())
#     cctimes         = Column(Integer())
#     ccblocktime     = Column(Integer())
#     brouteswitch    = Column(Integer())
#     brouteperiod    = Column(Integer())
#     broutetimes     = Column(Integer())
#     brouteurls      = Column(String())
#     brouteblocktime = Column(Integer())
#
#     def __repr__(self):
#         return "<t_ccset(id='%s')>" % (self.id,)

class SiteStatus(Base):
    __tablename__ = "t_sitestatus"

    id = Column(Integer(), primary_key=True)
    url = Column(String())
    time = Column(Integer())
    status = Column(Integer())
    result = Column(Integer())
    desc = Column(String())
    protype = Column(String())
    freq = Column(Integer())
    rate = Column(Integer())
    responsetime = Column(Float())
    type = Column(Integer())

    def __repr__(self):
        return "<t_sitestatus(id='%s')>" % (self.id,)


# class SecuritySet(Base):
#     __tablename__ = "t_securityset"
#
#     id = Column(Integer(), primary_key=True)
#     is_ssl = Column(Integer())
#     ssl_path = Column(String())
#     header_hide_list = Column(String())
#     spider_list = Column(String())
#     hostlinking_list = Column(String())
#     is_sensitive = Column(Integer())
#     sensitive_words = Column(String())
#     is_selfstudy = Column(Integer())
#     is_autodefence = Column(Integer())
#     autodefence_cycle = Column(Integer())
#     autodefence_count = Column(Integer())
#     autodefence_second = Column(Integer())
#     is_bypass = Column(Integer())
#     is_autodiskclean = Column(Integer())
#     autodiskclean = Column(Integer())
#
#     def __repr__(self):
#         return "<t_securityset(id='%s')>" % (self.id,)


class SelfStudyRule(Base):
    __tablename__ = "t_selfstudyrule"

    id = Column(Integer(), primary_key=True)
    ruleid = Column(Integer())
    realruleid = Column(Integer())
    is_use = Column(Integer())
    uri = Column(String())
    host = Column(String())
    sourceip = Column(String())
    sourceport = Column(String())

    def __repr__(self):
        return "<t_selfstudyrule(id='%s')>" % (self.id,)


# class SelfStudySetting(Base):
#     __tablename__ = "t_selfstudy_setting"
#
#     id                 = Column(Integer(),primary_key=True)
#     is_use             = Column(Integer())
#     is_ip_white        = Column(Integer())
#     is_ip_black        = Column(Integer())
#     is_domain_black    = Column(Integer())
#     is_use_result      = Column(Integer())
#
#     def __repr__(self):
#         return "<t_selfstudy_setting(id='%s')>" % (self.id,)

class SelfStudyIPWhite(Base):
    __tablename__ = "t_selfstudy_ip_white"

    id = Column(Integer(), primary_key=True)
    is_use = Column(Integer())
    ip = Column(String())

    def __repr__(self):
        return "<t_selfstudy_ip_white(id='%s')>" % (self.id,)


class SelfStudyResult(Base):
    __tablename__ = "t_selfstudy_result"

    id                 = Column(Integer(),primary_key=True)
    uri_max            = Column(Integer())
    arg_name_max       = Column(Integer())
    arg_content_max    = Column(Integer())
    arg_count_max      = Column(Integer())
    cookie_max         = Column(Integer())
    cookie_name_max    = Column(Integer())
    cookie_content_max = Column(Integer())
    cookie_count_max   = Column(Integer())

    def __repr__(self):
        return "<t_selfstudy_result(id='%s')>" % (self.id,)

class DevInfo(Base):
    __tablename__ = "t_devinfo"

    model = Column(String(), primary_key=True)
    sys_ver = Column(String())
    rule_ver = Column(String())
    serial_num = Column(String())

    def __repr__(self):
        return "<t_devinfo(id='%s')>" % (self.id,)


class VlanInfo(Base):
    __tablename__ = 't_vlan'

    nets = Column(String())
    ip = Column(String())
    vlan_id = Column(String())
    id = Column(Integer(), primary_key=True)

    def __repr__(self):
        return "<t_vlan(nets='%s',vlan_id='%s')>" % (self.nets, self.vlan_id)


class BridgeMulIP(Base):
    __tablename__ = 't_bridge_mulip'

    id = Column(Integer(), primary_key=True)
    nic = Column(String())
    ip = Column(String())
    mask = Column(String())

    def __repr__(self):
        return "<t_bridge_mulip(nic=%s,ip=%s,mask=%s)>" % (self.nic, self.ip, self.mask)


class WebMonitor(Base):
    __tablename__ = "t_web_connections"

    id = Column(Integer(), primary_key=True)
    sWebSiteName = Column(String())
    iConConnections = Column(Integer())
    iNewConnections = Column(Integer())
    iTransactions = Column(Integer())
    iTime = Column(Integer())
    siteflow = Column(Integer())

    def __repr__(self):
        return "<t_web_connections(id='%s')>" % (self.id,)


class Website(Base):
    __tablename__ = "t_website"

    id = Column(Integer(), primary_key=True)
    sGroupName = Column(String())
    sWebSiteName = Column(String())
    sWebSiteIP = Column(String())
    iWebSitePort = Column(Integer())
    isproxy = Column(Integer())
    ruleModelId = Column(Integer)
    selfRuleModelId = Column(Integer)

    # sWebSiteProtocol = Column(String())
    # sWebSiteLoadBalance = Column(String())
    # iIsCache = Column(Integer())
    # iHealthExamination = Column(Integer())
    # iARPOnOff = Column(Integer())
    # # iWebSiteLocalPort = Column(Integer())
    # # sWebSiteServerPem = Column(String())
    # # sWebSiteServerKey = Column(String())
    # sWebSiteOs = Column(String())
    # sWebSiteDb = Column(String())
    # sDevelopmentLanguage = Column(String())
    # sWebSiteRemark = Column(String())
    # sWebSiteServer = Column(String())

    def __repr__(self):
        return "<t_website(id='%s')>" % (self.id,)


class RuleModel(Base):
    __tablename__ = "t_rule_model"

    id = Column(Integer, primary_key=True)
    rule = Column(Integer)
    type = Column(Integer)
    groupModelId = Column(Integer)
    different = Column(Integer)
    name = Column(String(100))
    remark = Column(String(355))
    ischecked = Column(SmallInteger)
    confName = Column(String(355))
    isDefault = Column(Integer)

    def __repr__(self):
        return "<t_rule_model(id='%s')" % self.id


class RecordHistory(Base):
    __tablename__ = "t_record_history"

    id = Column(Integer(), primary_key=True)
    new_table_name = Column(String())
    start_time = Column(Integer())
    end_time = Column(Integer())
    ori_table_name = Column(String())

    def __repr__(self):
        return "<t_record_history(id='%s')>" % self.id


class WebsiteServers(Base):
    __tablename__ = "t_website_servers"

    id = Column(Integer(), primary_key=True)
    ip = Column(String())
    port = Column(String())
    protocol = Column(String())
    os = Column(String())
    db = Column(String())
    webServer = Column(String())
    developmentLanguage = Column(String())
    webSiteId = Column(Integer())

    def __repr__(self):
        return "<t_website_servers(id='%s')>" % self.id


class RuleCustomDefendPolicy(Base):
    __tablename__ = "rule_custom_defend_policy"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    rule = Column(Text)
    status = Column(String(1))
    source_ip = Column(String(255))
    destination_ip = Column(String(255))
    destination_url = Column(String(255))

    def __repr__(self):
        return "<rule_custom_defend_policy(id='%s',name='%s'" % (self.id, self.name)


# class IpFilterSet(Base):
#     __tablename__ = "t_ip_filter_set"
#
#     id = Column(Integer, primary_key=True)
#     ip_addr_start = Column(String(200))
#     ip_addr_end = Column(String(200))
#     status = Column(Integer)
#     add_time = Column(Integer)
#
#     def __repr__(self):
#         return "<t_ip_filter_set(id='%s',ip_addr_start='%s',ip_addr_end='%s',status='%s',add_time='%s'" % (
#                 self.id,self.ip_addr_start,self.ip_addr_end,self.status,self.add_time)


class Uploadedfilelogs(Base):
    __tablename__ = "t_uploadedfilelogs"

    id = Column(Integer, primary_key=True)
    reporttime = Column(Integer)
    url = Column(String(64))
    filename = Column(String(128))
    uploadtime = Column(Integer)
    type = Column(Integer)
    rating = Column(String(16))

    def __repr__(self):
        return "<t_uploadedfilelogs(id='%s',reporttime='%s',url='%s',filename='%s',\
                uploadtime='%s',type='%s',rating='%s'" % (self.id, self.reporttime,
                                                          self.url, self.filename, self.uploadtime, self.type,
                                                          self.rating)


class Viruslogs(Base):
    __tablename__ = "t_viruslogs"

    id = Column(Integer, primary_key=True)
    downloadPath = Column(String(255))
    uploadFileID = Column(Integer)
    result = Column(Text)

    def __repr__(self):
        return "<t_viruslogs(id='%s',downloadPath='%s',uploadFileID='%s',result='%s'" % (
        self.id, self.downloadPath, self.uploadFileID, self.result)


# class IntelligentTrojanHorseSet(Base):
#     __tablename__ = "t_intelligent_Trojan_horse_set"
#
#     id = Column(Integer, primary_key=True)
#     status = Column(Integer)
#     interceptedFileSuffix = Column(String(512))
#     fileSize = Column(Integer)
#     addTime = Column(Integer)
#
#     def __repr__(self):
#         return ("<t_intelligent_Trojan_horse_set(id='%s',status='%s',"
#                 "interceptedFileSuffix='%s',fileSize='%s',addTime='%s'" %
#                 (self.id,self.status,self.interceptedFileSuffix,self.fileSize,self.addTime))


if __name__ == '__main__':
    session = Session()
    a = session.query(Rules).all()
    for c in a:
        print c.id, c.name
    session.close()
