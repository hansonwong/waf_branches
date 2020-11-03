#!/usr/bin/env/python
# *-* coding: utf-8 *-*

# Copyright (C) 1998-2015 Bluedon. All Rights Reserve
# This file is part of Bluedon Firewall

import os
import subprocess
import sqlalchemy
#from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,SmallInteger,BigInteger,Index,DateTime
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#from sqlalchemy.orm import Session
#from sqlalchemy import PrimaryKeyConstraint
import pdb
import json
from networking.devices import devices

__all__ = ["Session", "net_interface", "get_interfaces_all", "get_interface_at",
           "iface_aggregation"]

Base = declarative_base()
#Base = automap_base()
constr = "mysql://root:bd_123456@localhost/db_firewall?unix_socket=/tmp/mysql3306.sock"
engine = create_engine(constr, encoding='utf-8', echo=False)
Session = sessionmaker(bind=engine)
#Base.prepare(engine, reflect=True)
MainSession = Session()


"""class net_interface(Base):

    __tablename__="m_tbnetport"
    id =                        Column(Integer, primary_key=True)
    sPortName =                 Column(String(128))
    sNetMask =                  Column(String(64))
    sWorkMode =                 Column(String(64))
    iByManagement =             Column(SmallInteger)
    iAllowPing =                Column(SmallInteger)
    iAllowTraceRoute =          Column(SmallInteger)
    iIPV4ConnectionType =       Column(SmallInteger)
    sIPV4Address =              Column(String(64))
    sIPV4NextJump =             Column(String(64))
    iIPV6ConnectionType =       Column(SmallInteger)
    sIPV6Address =              Column(String(64))
    sIPV6NextJump =             Column(String(64))
    iStatus =                   Column(SmallInteger, default=0)
    def __repr__(self):
        return "<m_tbnetport(id=%d,sPortName='%s',sNetMask='%s',sWorkMode='%s'," \
               "iByManagement=%d, iAllowPing=%d,iAllowTraceRoute=%d,iIPV4ConnectionType=%d" \
               "sIPV4Address='%s', sIPV4NextJump='%s',iIPV6ConnectionType=%d" \
               "sIPV6Address='%s', sIPV6NextJump ='%s',iStatus=%d" % \
                (self.id,self.sPortName,self.sNetMask,self.sWorkMode,self.iByManagement,self.iAllowPing
         ,self.iAllowTraceRoute,self.iIPV4ConnectionType,self.sIPV4Address,self.sIPV4NextJump,self.iIPV6ConnectionType,
self.sIPV6Address,self.sIPV6NextJump,self.iStatus)"""

def insert_interfaces():
    ifaces = devices().get_interfaces()
    session = Session()
    for instance in session.query(net_interface):
        session.delete(instance)
    for iface in ifaces:
        session.add(net_interface(sPortName='%s'%iface))
    session.commit()
    session.close()

"""class tb_iface_aggregation(Base):
    __tablename__="m_tbportaggregation"
    id =                Column(Integer, primary_key=True)
    sBridgeName =       Column(String(64))
    sBindDevices =       Column(String(512))
    iByManagement =       Column(SmallInteger)
    iAllowPing =       Column(SmallInteger)
    iAllowTraceRoute =       Column(SmallInteger)
    sIPV4Type =       Column(String(32))
    sIPV4 =       Column(String(32))
    sIPV4Mask =       Column(String(32))
    sIPV6Type =       Column(String(32))
    sIPV6 =       Column(String(32))
    sIPV6Mask =       Column(String(32))
    iStatus =       Column(SmallInteger)
    sWorkMode =       Column(String(32))
    sGetIP =       Column(String(32))
    def __repr__(self):
        return "<m_tbportaggregation(id=%d,sBridgeName='%s',sBindDevices='%s'," \
               "iByManagement=%d, iAllowPing=%d,iAllowTraceRoute=%d,sIPV4Type='%s'" \
               "sIPV4='%s', sIPV4Mask='%s',sIPV6Type='%s'" \
               "sIPV6='%s', sIPV6Mask ='%s',iStatus=%d, sWorkMode='%s', sGetIP='%s'" % \
                (self.id,self.sBridgeName,self.sBindDevices,self.iByManagement,self.iAllowPing
         ,self.iAllowTraceRoute,self.sIPV4Type,self.sIPV4,self.sIPV4Mask,self.sIPV6Type,
         self.sIPV6,self.sIPV6Mask,self.iStatus,self.sWorkMode, self.sGetIP)




class tb_virutal_line(Base):
    __tablename__="m_tbvirtualline"
    id =                    Column(Integer, primary_key=True)
    sVirtualPortOne =       Column(String(32))
    sVirtualPortTwo =       Column(String(32))
    sDesc =                 Column(String(512))
    iStatus =               Column(SmallInteger)
    def __repr__(self):
        return "<m_tbvirtualline(id=%d,sVirtualPortOne='%s',sVirtualPortTwo='%s'," \
               "sDesc='%s',iStatus=%d" % (self.id, self.sVirtualPortOne, self.sVirtualPortTwo,
                                          self.sDesc, self.iStatus )

class tb_isproute(Base):
    __tablename__="m_tbisproute"
    id =                    Column(Integer, primary_key=True)
    sIspAddress =           Column(String(32))
    sNextJump =             Column(String(32))
    sOutPort =              Column(String(32))
    sMetric =               Column(String(64))
    sIPV =                  Column(String(16))
    iStatus =               Column(SmallInteger)
    def __repr__(self):
        return "<m_tbisproute(id=%d,sIspAddress='%s',sNextJump='%s'," \
               "sOutPort='%s',sMetric='%s',sIPV='%s',iStatus=%d" %\
               (self.id, self.sIspAddress,self.sNextJump,
                self.sOutPort, self.sMetric,self.sIPV, self.iStatus )

class tb_strategyroute(Base):
    __tablename__ = 'm_tbstrategyroute'
    id = Column(Integer, primary_key=True)
    sRouteName = Column(String(64))
    sPriority = Column(String(32))
    sSourceIP = Column(String(32))
    sTargetIP = Column(String(32))
    sDesc = Column(String(512))
    iProtocolApp = Column(SmallInteger)
    sProtocol = Column(String(64))
    sProtocolPort = Column(String(32))
    sApplication = Column(String(64))
    iIfaceJump = Column(SmallInteger)
    sIfaceName = Column(String(32))
    sJumpName = Column(String(64))
    sIPV = Column(String(16))
    iStatus = Column(SmallInteger)

    def __repr__(self):
        return "<m_tbstrategyroute(id=%d,sRouteName='%s',sPriority='%s'," \
               "sSourceIP='%s',sTargetIP='%s',sDesc='%s',iProtocolApp = %d," \
               "sProtocol='%s', sProtocolPort='%s', sApplication='%s'," \
               "iIfaceJump=%d, sIfaceName='%s',sJumpName='%s'," \
               "sIPV='%s',iStatus=%d" %\
               (self.id, self.sRouteName,self.sPriority,self.sSourceIP,
                self.sTargetIP, self.sDesc,self.iProtocolApp, self.sProtocol,
                self.sProtocolPort,self.sApplication,self.iIfaceJump,
                self.sIfaceName,self.sJumpName,self.sIPV,self.iStatus)

#CREATE TABLE m_tbservices_list
#(
    #id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    #sSourcePortLow VARCHAR(64),
    #sSourcePortHigh VARCHAR(64),
    #sTargetPortLow VARCHAR(64),
    #sTargetPortHigh VARCHAR(64),
    #sProtocol VARCHAR(128),
    #sServiceName VARCHAR(255),
    #iGroupID INT,
    #sMark VARCHAR(255)
#);

class tb_services_list(Base):
    __tablename__ = 'm_tbservices_list'
    id = Column(Integer, primary_key=True)
    sSourcePortLow = Column(String(64))
    sSourcePortHigh = Column(String(64))
    sTargetPortLow = Column(String(64))
    sTargetPortHigh = Column(String(64))
    sProtocol = Column(String(128))
    sServiceName = Column(String(255))
    iGroupID = Column(Integer, primary_key=True)
    sMark = Column(String(255))
    def __repr__(self):
        return "<m_tbservices_list(id=%d,sSourcePortLow='%s',sSourcePortHigh='%s'," \
               "sTargetPortLow='%s',sTargetPortHigh='%s',sProtocol='%s'," \
               "sServiceName = %s, iGroupID = %d, sMark = %s" %\
               (self.id, self.sSourcePortLow,self.sSourcePortHigh,self.sTargetPortLow,
                self.sTargetPortHigh, self.sProtocol,self.sServiceName, self.iGroupID,
                self.sMark)"""


class net_interface_arg:
    def __init__(self):
        self.id =                        0
        self.sPortName =                 ''
        self.sNetMask =                  ''
        self.sWorkMode =                 ''
        self.iByManagement =             ''
        self.iAllowPing =                ''
        self.iAllowTraceRoute =          ''
        self.iIPV4ConnectionType =       ''
        self.sIPV4Address =              ''
        self.sIPV4NextJump =             ''
        self.iIPV6ConnectionType =       ''
        self.sIPV6Address =              ''
        self.sIPV6NextJump =             ''
        self.iStatus =                   ''

def convert_net_interface_arg(jsonstr):
    #print "********************",type(jsonstr)
    jsnobj=json.loads(jsonstr.replace('\r', ''), 'utf-8')
    ins = net_interface_arg()
    ins.id = jsnobj['id']
    ins.sPortName = jsnobj['sPortName']
    ins.sNetMask = jsnobj['sNetMask']
    ins.sWorkMode = jsnobj['sWorkMode']
    ins.iByManagement = jsnobj['iByManagement']
    ins.iAllowPing = jsnobj['iAllowPing']
    ins.iAllowTraceRoute = jsnobj['iAllowTraceRoute']
    ins.iAllowFlow  = jsnobj['iAllowFlow']
    ins.iIPV4ConnectionType = jsnobj['iIPV4ConnectionType']
    ins.sIPV4Address =            jsnobj['sIPV4Address']
    ins.sIPV4NextJump = jsnobj['sIPV4NextJump']
    ins.iIPV6ConnectionType = jsnobj['iIPV6ConnectionType']
    ins.sIPV6Address = jsnobj['sIPV6Address']
    ins.sIPV6NextJump = jsnobj['sIPV6NextJump']
    ins.iStatus = jsnobj['iStatus']
    return ins

class virtual_line_arg:
    def __init__(self):
        self.id =                    Column(Integer, primary_key=True)
        self.sVirtualPortOne =       Column(String(32))
        self.sVirtualPortTwo =       Column(String(32))
        self.sDesc =                 Column(String(512))
        self.iStatus =               Column(SmallInteger)

def convert_virtual_line_arg(jsonstr):
    jsnobj=json.loads(jsonstr.replace('\r', ''), 'utf-8')
    ins = virtual_line_arg()
    ins.id = int(jsnobj['id'])
    ins.sVirtualPortOne = jsnobj['sVirtualPortOne']
    ins.sVirtualPortTwo = jsnobj['sVirtualPortTwo']
    ins.sDesc = jsnobj['sDesc']
    ins.iStatus = int(jsnobj['iStatus'])
    return ins

class isproute_arg:
    def __init__(self):
        self.id =                    Column(Integer, primary_key=True)
        self.sIspAddressID =         Column(Integer)
        self.sIspAddress =           Column(String(32))
        self.sNextJump =             Column(String(32))
        self.sOutPort =              Column(String(32))
        self.sMetric =               Column(String(64))
        self.sIPV =                  Column(String(16))
        self.iStatus =               Column(SmallInteger)
        self.iPortType =             Column(SmallInteger)

def convert_isproute_arg(jsonstr):
    jsnobj=json.loads(jsonstr.replace('\r', ''), 'utf-8')
    ins = isproute_arg()
    ins.id = int(jsnobj['id'])
    ins.sIspAddressID = int(jsnobj['sIspAddressID'])
    ins.sIspAddress = jsnobj['sIspAddress']
    ins.sNextJump = jsnobj['sNextJump']
    ins.sOutPort = jsnobj['sOutPort']
    ins.sMetric = jsnobj['sMetric']
    ins.sIPV = jsnobj['sIspAddress']
    ins.iStatus = int(jsnobj['iStatus'])
    ins.iPortType = int(jsnobj['iPortType'])
    return ins

class iface_aggregation_arg():
    def __init__(self):
        self.id =                ''
        self.sBridgeName =       ''
        self.sBindDevices =       ''
        self.iByManagement =       ''
        self.iAllowPing =       ''
        self.iAllowTraceRoute =       ''
        self.sIPV4Type =       ''
        self.sIPV4 =       ''
        self.sIPV4Mask =       ''
        self.sIPV6Type =       ''
        self.sIPV6 =       ''
        self.sIPV6Mask =       ''
        self.iStatus =       ''
        self.sWorkMode =       ''
        self.sGetIP =       ''
        self.sIPV4Gw =      ''

def convert_iface_aggregation_arg(jsonstr):
    jsnobj=json.loads(jsonstr.replace('\r', ''), 'utf-8')
    ins = iface_aggregation_arg()
    ins.id =                int(jsnobj['id'])
    ins.sBridgeName =       jsnobj['sBridgeName']
    ins.sBindDevices =       jsnobj['sBindDevices']
    ins.iByManagement =       int(jsnobj['iByManagement'])
    ins.iAllowPing =       int(jsnobj['iAllowPing'])
    ins.iAllowTraceRoute =       int(jsnobj['iAllowTraceRoute'])
    ins.sIPV4Type =       jsnobj['sIPV4Type']
    ins.sIPV4 =       jsnobj['sIPV4']
    ins.sIPV4Mask =       jsnobj['sIPV4Mask']
    ins.sIPV6Type =       jsnobj['sIPV6Type']
    ins.sIPV6 =       jsnobj['sIPV6']
    ins.sIPV6Mask =       jsnobj['sIPV6Mask']
    ins.iStatus =       int(jsnobj['iStatus'])
    ins.sIPV4Gw =      jsnobj['sIPV4Gw']
    #ins.sWorkMode =       jsnobj['sWorkMode']
    # ins.sGetIP =       jsnobj['sGetIP']
    return ins

class strategyroute_arg:
    def __init__(self):
        self.id = Column(Integer, primary_key=True)
        self.sRouteName = Column(String(64))
        self.sPriority = Column(String(32))
        self.iSourceIPID = Column(Integer)
        self.sSourceIPAddr = Column(String(32))
        self.iTargetIPID = Column(Integer)
        self.sTargetIPAddr = Column(String(32))
        self.sDesc = Column(String(512))
        self.iProtocolApp = Column(SmallInteger)
        self.sProtocol = Column(String(64))
        self.iSourcePort = Column(Integer)
        self.iTargetPort = Column(Integer)
        self.iApplicationID = Column(Integer)
        self.sApplicationName = Column(String(64))
        self.iIfaceJump = Column(SmallInteger)
        self.iIfaceID = Column(Integer)
        self.sIfaceName = Column(String(32))
        self.sJumpName = Column(String(64))
        self.sIPV = Column(String(16))
        self.iStatus = Column(SmallInteger)

def convert_strategyroute_arg(jsonstr):
    #jsnobj=json.loads(jsonstr.replace('\r', ''), 'utf-8')
    jsonobj = json.loads(jsonstr)
    ins = strategyroute_arg()
    ins.id = int(jsonobj['id'])
    ins.sRouteName = jsonobj['sRouteName']
    ins.sPriority = jsonobj['sPriority']
    ins.iSourceIPID = jsonobj['iSourceIPID']
    ins.sSourceIPAddr = jsonobj['sSourceIPAddr']
    ins.iTargetIPID = jsonobj['iTargetIPID']
    ins.sTargetIPAddr = jsonobj['sTargetIPAddr']
    ins.sDesc = jsonobj['sDesc']
    ins.iProtocolApp = int(jsonobj['iProtocolApp'])
    ins.sProtocol = jsonobj['sProtocol']
    ins.iSourcePort = jsonobj['iSourcePort']
    ins.iTargetPort = jsonobj['iTargetPort']
    ins.iApplicationID = jsonobj['iApplicationID']
    ins.sApplicationName = jsonobj['sApplicationName']
    ins.iIfaceJump = jsonobj['iIfaceJump']
    ins.iIfaceID = jsonobj['iIfaceID']
    ins.sIfaceName = jsonobj['sIfaceName']
    ins.sJumpName = jsonobj['sJumpName']
    ins.sIPV = jsonobj['sIPV']
    ins.iStatus = jsonobj['iStatus']
    return ins


if __name__=="__main__":
    pass
    #print(get_interfaces_all())
    #print(get_interface_at(1))
    #print(get_iface_aggregation_at(2))
    #print(insert_interfaces())
    #print(get_all(tb_iface_aggregation))
