# -*- coding: utf-8 -*-

from db import Base
from sqlalchemy import Column, Integer, String, SmallInteger, BigInteger


class NetPort(Base):
    __tablename__ = "m_tbnetport"
    id =                        Column(Integer, primary_key=True)
    sPortName =                 Column(String(128))
    sNetMask =                  Column(String(64))
    sWorkMode =                 Column(String(64))
    iByManagement =             Column(SmallInteger)
    iSSH =                      Column(SmallInteger)
    iWeb =                      Column(SmallInteger)
    iAllowPing =                Column(SmallInteger)
    iAllowTraceRoute =          Column(SmallInteger)
    iAllowFlow     =            Column(SmallInteger)
    iIPV4ConnectionType =       Column(SmallInteger)
    sIPV4Address =              Column(String(512))
    sIPV4NextJump =             Column(String(32))
    iIPV6ConnectionType =       Column(SmallInteger)
    sIPV6Address =              Column(String(512))
    sIPV6NextJump =             Column(String(32))
    iStatus =                   Column(String(11))
    iMAC =                      Column(String(100))
    sLan =                      Column(String(10))

    def __repr__(self):
        return "<m_tbnetport(id=%d,sPortName='%s',sNetMask='%s',sWorkMode='%s'," \
               "iByManagement=%s, iSSH=%s, iWeb=%s, iAllowPing=%s,iAllowTraceRoute=%s,iAllowFlow=%s,iIPV4ConnectionType=%s" \
               "sIPV4Address='%s', sIPV4NextJump='%s',iIPV6ConnectionType=%s" \
               "sIPV6Address='%s', sIPV6NextJump ='%s',iStatus=%s,iMAC='%s',sLan='%s'" % ( 
                self.id, self.sPortName, self.sNetMask, self.sWorkMode,
                self.iByManagement, self.iSSH, self.iWeb, self.iAllowPing, self.iAllowFlow,
                self.iAllowTraceRoute, self.iIPV4ConnectionType,
                self.sIPV4Address, self.sIPV4NextJump, self.iIPV6ConnectionType,
                self.sIPV6Address, self.sIPV6NextJump, self.iStatus, self.iMAC,
                self.sLan)


class AddressList(Base):
    __tablename__ = "m_tbaddress_list"

    id = Column(Integer, primary_key=True)
    sAddressname = Column(String(255))
    sAddress = Column(String(512))
    sIPV = Column(String(32))
    sNetmask = Column(String(255))
    sAddtype = Column(String(255))
    sMark = Column(String(255))
    sInserttime = Column(String(12))
    sUpdatetime = Column(String(12))
    IpgroupId = Column(Integer)
    sIPJson = Column(String(255))

    def __repr__(self):
        return "<m_tbaddress_list(id='%s',sAddressname='%s',sAddress='%s',sIPV='%s',sNetmask='%s',sAddtype='%s',sMark='%s',sInserttime='%s',sUpdatetime='%s',IpgroupId='%s',sIPJson='%s'" % (self.id,self.sAddressname,self.sAddress,self.sIPV,self.sNetmask,self.sAddtype,self.sMark,self.sInserttime,self.sUpdatetime,self.IpgroupId,self.sIPJson)


class Searitystrate(Base):
    __tablename__ = "m_tbSearitystrate"

    id = Column(Integer, primary_key=True)
    sStrategyName = Column(String(255))
    sInputPort = Column(String(64))
    sOutPort = Column(String(64))
    sSourceValue = Column(String(255))
    iSourceType = Column(Integer)
    sTargetValue = Column(String(255))
    iTargetIPType = Column(Integer)
    sProtocol = Column(String(64))
    sSourcePort = Column(Integer)
    sTargetPort = Column(Integer)
    iEffectiveTime = Column(Integer)
    iEffectiveTimeType = Column(Integer)
    sMark = Column(String(255))
    sAppName = Column(String(255))
    iAppID = Column(Integer)
    iAction = Column(Integer)
    iLog = Column(Integer)
    iSort = Column(Integer)
    iStatus = Column(Integer)
    iOneway = Column(Integer)
    sIPV = Column(String(10))
    tuozhan = Column(String(5))
    sSourceMac = Column(String(96))
    sTargetMac = Column(String(96))
    sService = Column(String(128))
    iServiceType = Column(Integer)

    def __repr__(self):
        return "<m_tbSearitystrate(id='%s',sStrategyName='%s',sInputPort='%s',sOutPort='%s',sSourceValue='%s',iSourceType='%s',sTargetValue='%s',iTargetIPType='%s',sProtocol='%s',sSourcePort='%s',sTargetPort='%s',iEffectiveTime='%s',iEffectiveTimeType='%s',sMark='%s',sAppName='%s',iAppID='%s',iAction='%s',iLog='%s',iSort='%s',iStatus='%s',iOneway='%s',sIPV='%s',tuozhan='%s',sSourceMac='%s',sTargetMac='%s',sService='%s',iServiceType='%s'" % (self.id,self.sStrategyName,self.sInputPort,self.sOutPort,self.sSourceValue,self.iSourceType,self.sTargetValue,self.iTargetIPType,self.sProtocol,self.sSourcePort,self.sTargetPort,self.iEffectiveTime,self.iEffectiveTimeType,self.sMark,self.sAppName,self.iAppID,self.iAction,self.iLog,self.iSort,self.iStatus,self.iOneway,self.sIPV,self.tuozhan,self.sSourceMac,self.sTargetMac,self.sService,self.iServiceType)


class Bridgedevice(Base):
    __tablename__ = "m_tbbridgedevice"

    id = Column(Integer, primary_key=True)
    sBridgeName = Column(String(64))
    sBindDevices = Column(String(512))
    iByManagement = Column(SmallInteger)
    iAllowPing = Column(SmallInteger)
    iAllowTraceRoute = Column(SmallInteger)
    iAllowLog = Column(SmallInteger)
    sIPV4 = Column(String(512))
    sIPV4Mask = Column(String(32))
    sIPV6 = Column(String(512))
    sIPV6Mask = Column(String(32))
    iStatus = Column(SmallInteger)
    iSSH = Column(SmallInteger)
    iWeb = Column(SmallInteger)
    bridgeType = Column(String(255))

    def __repr__(self):
        return "<m_tbbridgedevice(id='%s',sBridgeName='%s',sBindDevices='%s',iByManagement='%s',iAllowPing='%s',iAllowTraceRoute='%s',iAllowLog='%s',sIPV4='%s',sIPV4Mask='%s',sIPV6='%s',sIPV6Mask='%s',iStatus='%s',iSSH='%s',iWeb='%s',bridgeType='%s'" % (self.id,self.sBridgeName,self.sBindDevices,self.iByManagement,self.iAllowPing,self.iAllowTraceRoute,self.iAllowLog,self.sIPV4,self.sIPV4Mask,self.sIPV6,self.sIPV6Mask,self.iStatus,self.iSSH,self.iWeb,self.bridgeType)


class Virtualline(Base):
    __tablename__ = "m_tbvirtualline"

    id = Column(Integer, primary_key=True)
    sVirtualPortOne = Column(String(32))
    sVirtualPortTwo = Column(String(32))
    sDesc = Column(String(512))
    iStatus = Column(SmallInteger)

    def __repr__(self):
        return "<m_tbvirtualline(id='%s',sVirtualPortOne='%s',sVirtualPortTwo='%s',sDesc='%s',iStatus='%s'" % (self.id,self.sVirtualPortOne,self.sVirtualPortTwo,self.sDesc,self.iStatus)
