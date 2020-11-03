#-*-coding:utf-8-*-
import os, time, MySQLdb
from config import config

gettables = {}
waftables = {}
# Database: `logs`
# table `browser`
gettables['browser'] = '''CREATE TABLE IF NOT EXISTS `browser` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(25) COLLATE utf8_unicode_ci NOT NULL,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;'''

# table `daily`
gettables['daily'] = '''CREATE TABLE IF NOT EXISTS `daily` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `day` varchar(8) COLLATE utf8_unicode_ci NOT NULL,
  `visits` mediumint(8) unsigned NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `day` (`day`),
  KEY `domain` (`domain`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;'''

# table `domain`
gettables['domain'] = '''CREATE TABLE IF NOT EXISTS `domain` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `code` varchar(8) COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;'''

# table `errors`
gettables['errors'] = '''CREATE TABLE IF NOT EXISTS `errors` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `code` varchar(4) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

# table `errors404`
gettables['errors404'] = '''CREATE TABLE IF NOT EXISTS `errors404` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `referer` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

# table `filetypes`
gettables['filetypes'] = '''CREATE TABLE IF NOT EXISTS `filetypes` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `type` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `bwwithoutcompress` bigint(20) unsigned NOT NULL,
  `bwaftercompress` bigint(20) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

# table `general`
gettables['general'] = '''CREATE TABLE IF NOT EXISTS `general` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `visits` mediumint(8) unsigned NOT NULL,
  `visits_unique` mediumint(8) unsigned NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `pages_nv` mediumint(8) unsigned NOT NULL,
  `hits_nv` mediumint(8) unsigned NOT NULL,
  `bandwidth_nv` bigint(20) unsigned NOT NULL,
  `hosts_known` mediumint(8) unsigned NOT NULL,
  `hosts_unknown` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `year_monthed_2` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `domain_2` (`domain`),
  KEY `year_monthed_3` (`year_monthed`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

# table `hours`
gettables['hours'] = '''CREATE TABLE IF NOT EXISTS `hours` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `hour` tinyint(3) unsigned NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `domain` (`domain`),
  KEY `year_monthed` (`year_monthed`),
  KEY `year_monthed_2` (`year_monthed`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

# table `misc`
gettables['misc'] = '''CREATE TABLE IF NOT EXISTS `misc` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `text` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

# table `origin`
gettables['origin'] = '''CREATE TABLE IF NOT EXISTS `origin` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `fromed` varchar(5) COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

# table `os`
gettables['os'] = '''CREATE TABLE IF NOT EXISTS `os` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(25) COLLATE utf8_unicode_ci NOT NULL,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

# table `pageref`
gettables['pageref'] = '''CREATE TABLE IF NOT EXISTS `pageref` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `hits` (`hits`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

# table `robot`
gettables['robot'] = '''CREATE TABLE IF NOT EXISTS `robot` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `name` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(12) COLLATE utf8_unicode_ci NOT NULL,
  `hitsrobots` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `hits` (`hits`),
  KEY `domain` (`domain`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

# table `screen`
gettables['screen'] = '''CREATE TABLE IF NOT EXISTS `screen` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `size` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

# table `searchkeywords`
gettables['searchkeywords'] = '''CREATE TABLE IF NOT EXISTS `searchkeywords` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `words` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

# table `searchref`
gettables['searchref'] = '''CREATE TABLE IF NOT EXISTS `searchref` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `engine` varchar(25) COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `domain` (`domain`),
  KEY `year_monthed` (`year_monthed`),
  KEY `hits` (`hits`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

# table `searchwords`
gettables['searchwords'] = '''CREATE TABLE IF NOT EXISTS `searchwords` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `words` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

# table `session`
gettables['session'] = '''CREATE TABLE IF NOT EXISTS `session` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `ranged` varchar(12) COLLATE utf8_unicode_ci NOT NULL,
  `visits` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

# table `t_areas`
gettables['t_areas'] = '''CREATE TABLE IF NOT EXISTS `t_areas` (
  `Code` varchar(2) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `Province` varchar(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `Area` varchar(32) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `Desc` varchar(32) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`Code`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;'''

# table `t_auditlog`
gettables['t_auditlog'] = '''CREATE TABLE IF NOT EXISTS `t_auditlog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `time` int(11) NOT NULL,
  `username` varchar(16) DEFAULT NULL,
  `level1` varchar(10) DEFAULT NULL,
  `level2` varchar(10) DEFAULT NULL,
  `level3` varchar(10) DEFAULT NULL,
  `desc` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;'''

# table `t_countrycode`
gettables['t_countrycode'] = '''CREATE TABLE IF NOT EXISTS `t_countrycode` (
  `CountryCode` varchar(3) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `EnCountry` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `CnCountry` varchar(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `Continent` varchar(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`CountryCode`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;'''

# table `t_fileseat`
gettables['t_fileseat'] = '''CREATE TABLE IF NOT EXISTS `t_fileseat` (
  `logid` int(10) unsigned NOT NULL DEFAULT '0',
  `StdDir` varchar(50) NOT NULL,
  `Sdate` varchar(10) NOT NULL,
  `Stime` varchar(16) NOT NULL,
  PRIMARY KEY (`logid`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT='last time reading position';'''

# table `unkbrowser`
gettables['unkbrowser'] = '''CREATE TABLE IF NOT EXISTS `unkbrowser` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `agent` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `lastvisit` varchar(12) COLLATE utf8_unicode_ci NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

# table `unkos`
gettables['unkos'] = '''CREATE TABLE IF NOT EXISTS `unkos` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `agent` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `lastvisit` varchar(12) COLLATE utf8_unicode_ci NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

# table `webagent`
gettables['webagent'] = '''CREATE TABLE IF NOT EXISTS `webagent` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `miss` int(10) unsigned NOT NULL,
  `hit` int(10) unsigned NOT NULL,
  `bandwidth_miss` bigint(20) unsigned NOT NULL,
  `bandwidth_hit` bigint(20) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

# table `webvisit`
gettables['webvisit'] = '''CREATE TABLE IF NOT EXISTS `webvisit` (
  `visits` int(10) unsigned NOT NULL,
  `visits_unique` int(10) unsigned NOT NULL,
  `pages` int(10) unsigned NOT NULL,
  `attack` int(10) unsigned NOT NULL,
  `hit_times` int(10) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;'''

# table `worms`
gettables['worms'] = '''CREATE TABLE IF NOT EXISTS `worms` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `text` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(12) COLLATE utf8_unicode_ci NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;'''

countsety = '''(
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `logdate` date NOT NULL,
  `emergency` int(10) unsigned DEFAULT '0',
  `alert` int(10) unsigned DEFAULT '0',
  `critical` int(10) unsigned DEFAULT '0',
  `error` int(10) unsigned DEFAULT '0',
  `warning` int(10) unsigned DEFAULT '0',
  `notice` int(10) unsigned DEFAULT '0',
  `info` int(10) unsigned DEFAULT '0',
  `debug` int(10) unsigned DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `logdate` (`logdate`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='count severity' AUTO_INCREMENT=1 ;'''

ruleid = '''(
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `logdate` date NOT NULL,
  `ruleid` int(10) unsigned NOT NULL,
  `Hits` int(10) unsigned DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `logdate` (`logdate`),
  KEY `ruleid` (`ruleid`),
  KEY `Hits` (`hits`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='count rule id' AUTO_INCREMENT=1 ;'''

counturi = '''(
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `logdate` date NOT NULL,
  `Uri` varchar(512) DEFAULT NULL,
  `QueryString` varchar(512) DEFAULT NULL,
  `Host` varchar(255) DEFAULT NULL,
  `Hits` int(10) DEFAULT '1',
  `urlmd5` char(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `QueryString` (`QueryString`(333)),
  KEY `Uri` (`Uri`(333)),
  KEY `Host` (`Host`),
  KEY `logdate` (`logdate`),
  KEY `urlmd5` (`urlmd5`),
  KEY `Hits` (`Hits`),
  FULLTEXT KEY `Uri_2` (`Uri`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT='count uri times' AUTO_INCREMENT=1 ;'''

sourceip = '''(
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `logdate` date NOT NULL,
  `CountryCode` varchar(3) DEFAULT NULL,
  `RegionCode` varchar(8) DEFAULT NULL,
  `City` varchar(32) DEFAULT NULL,
  `SourceIP` varchar(15) NOT NULL,
  `Hits` int(10) unsigned DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `logdate` (`logdate`),
  KEY `SourceIP` (`SourceIP`),
  KEY `Hits` (`Hits`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='count sourceip' AUTO_INCREMENT=1 ;'''

alertlog = '''(
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `AuditLogID` int(10) unsigned NOT NULL DEFAULT '1',
  `AuditLogUniqueID` varchar(40) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `GeneralMsg` varchar(512) DEFAULT NULL,
  `Rulefile` varchar(255) NOT NULL,
  `RuleID` varchar(6) DEFAULT NULL,
  `MatchData` varchar(256) DEFAULT NULL,
  `Rev` varchar(128) DEFAULT NULL,
  `Msg` varchar(100) DEFAULT NULL,
  `Severity` varchar(16) DEFAULT NULL,
  `Tag1` varchar(68) DEFAULT NULL,
  `Tag2` varchar(68) DEFAULT NULL,
  `Tag3` varchar(68) DEFAULT NULL,
  `Status` varchar(8) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `RuleID` (`RuleID`),
  KEY `Severity` (`Severity`),
  KEY `AuditLogID` (`AuditLogID`),
  KEY `Status` (`Status`)
)ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='alert logs' AUTO_INCREMENT=1 ;'''

accesslog = '''(
  `AuditLogID` int(10) unsigned NOT NULL,
  `AuditLogUniqueID` varchar(40) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
  `AuditLogDate` date NOT NULL,
  `AuditLogTime` time NOT NULL,
  `CountryCode` varchar(3) DEFAULT NULL,
  `RegionCode` varchar(8) DEFAULT NULL,
  `City` varchar(32) DEFAULT NULL,
  `SourceIP` varchar(15) NOT NULL,
  `SourcePort` varchar(8) DEFAULT NULL,
  `DestinationIP` varchar(15) NOT NULL,
  `DestinationPort` varchar(8) DEFAULT NULL,
  `Referer` varchar(255) DEFAULT NULL,
  `UserAgent` varchar(255) DEFAULT NULL,
  `HttpMethod` varchar(8) DEFAULT NULL,
  `Uri` varchar(512) DEFAULT NULL,
  `QueryString` varchar(512) DEFAULT NULL,
  `HttpProtocol` varchar(16) DEFAULT NULL,
  `Host` varchar(255) DEFAULT NULL,
  `RequestContentType` varchar(255) DEFAULT NULL,
  `ResponseContentType` varchar(255) DEFAULT NULL,
  `HttpStatusCode` varchar(4) DEFAULT NULL,
  PRIMARY KEY (`AuditLogID`),
  KEY `SourceIP` (`SourceIP`),
  KEY `DestinationIP` (`DestinationIP`),
  KEY `HttpMethod` (`HttpMethod`),
  KEY `Host` (`Host`),
  KEY `alDate` (`AuditLogDate`,`AuditLogTime`),
  KEY `Uri` (`Uri`(333)),
  KEY `QueryString` (`QueryString`(333)),
  KEY `DestinationPort` (`DestinationPort`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access logs';'''

pages = '''(
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `url` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `entry` mediumint(8) unsigned NOT NULL,
  `exited` mediumint(8) unsigned NOT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `url` (`url`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access pages' AUTO_INCREMENT=1 ;'''

visitors = '''(
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `year_monthed` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `host` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `country_code` varchar(8) COLLATE utf8_unicode_ci DEFAULT NULL,
  `country_name` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `province` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `city` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `pages` mediumint(8) unsigned NOT NULL,
  `hits` mediumint(8) unsigned NOT NULL,
  `bandwidth` bigint(20) unsigned NOT NULL,
  `lastvisit` varchar(14) COLLATE utf8_unicode_ci NOT NULL,
  `startlastvisit` varchar(14) COLLATE utf8_unicode_ci DEFAULT NULL,
  `lastpage` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `domain` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `year_monthed` (`year_monthed`),
  KEY `domain` (`domain`),
  KEY `country_name` (`country_name`),
  KEY `province` (`province`),
  KEY `host` (`host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='access visitors' AUTO_INCREMENT=1 ;'''

# table `t_syslog`
syslog = '''(
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `time` datetime NOT NULL,
  `program` varchar(32) DEFAULT NULL COMMENT 'event type',
  `Severity` varchar(16) DEFAULT NULL,
  `desc` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;'''

#ddos attack table
ddoslog = '''(
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `logtime` int(10) NOT NULL,
  `srcip` varchar(15) NOT NULL,
  `CountryCode` varchar(3) DEFAULT NULL,
  `RegionCode` varchar(8) DEFAULT NULL,
  `City` varchar(32) DEFAULT NULL,
  `dstip` varchar(15) NOT NULL,
  `dstport` varchar(6) DEFAULT NULL,
  `protocol` varchar(8) DEFAULT NULL,
  `desc` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `logtime` (`logtime`),
  KEY `protocol` (`protocol`),
  KEY `dstport` (`dstport`),
  KEY `dstip` (`dstip`),
  KEY `srcip` (`srcip`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='ddos logs' AUTO_INCREMENT=1 ;'''

#weboutlog table
weboutlog = '''(
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dt` datetime DEFAULT NULL,
  `sip` varchar(15) DEFAULT '' COMMENT 'source ip',
  `dip` varchar(15) DEFAULT '' COMMENT 'dest ip',
  `sport` varchar(5) DEFAULT '' COMMENT 'source port',
  `dport` varchar(5) DEFAULT '' COMMENT 'dest port',
  `action` tinyint(4) DEFAULT '0' COMMENT '0 1',
  `number` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `number` (`number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;'''

#waftables['t_advance'] = '''CREATE TABLE IF NOT EXISTS `t_advance` (
#  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
#  `packet` int(10) DEFAULT 10000,
#  `length` int(10) DEFAULT 1460,
#  `enable` int(10) DEFAULT 0,
#  PRIMARY KEY (`id`)
#) ENGINE=MyISAM DEFAULT CHARSET=utf8 COMMENT='fragment set' AUTO_INCREMENT=1 ;'''
# insert table `t_advance`
#inadvance = '''INSERT INTO `t_advance`(`packet`, `length`, `enable`) 
#    VALUES(10000, 1450, 0);'''


# insert table `t_fileseat`
infileseat = '''INSERT INTO `t_fileseat` (`logid`, `StdDir`, `Sdate`, `Stime`) VALUES
(0, '/usr/local/bluedon/bdwaf/logs/audit/', '20140501', '20140501-0000');'''

# insert table `t_areas`
inareas = '''INSERT INTO `t_areas` (`Code`, `Province`, `Area`, `Desc`) VALUES
('01', 'Anhui', 'East China', '华东地区:安徽'),
('02', 'Zhejiang', 'East China', '华东地区:浙江'),
('03', 'Jiangxi', 'Central China', '华中地区:江西'),
('04', 'Jiangsu', 'East China', '华东地区:江苏'),
('05', 'Jilin', 'Northeast', '东北地区:吉林'),
('06', 'Qinghai', 'Northwest', '西北地区:青海'),
('07', 'Fujian', 'East China', '华东地区:福建'),
('08', 'Heilongjiang', 'Northeast', '东北地区:黑龙江'),
('09', 'Henan', 'Central China', '华中地区:河南'),
('10', 'Hebei', 'North China', '华北地区:河北'),
('11', 'Hunan', 'Central China', '华中地区:湖南'),
('12', 'Hubei', 'Central China', '华中地区:湖北'),
('13', 'Xinjiang', 'Northwest', '西北地区:新疆'),
('14', 'Xizang', 'Southwest', '西南地区:西藏'),
('15', 'Gansu', 'Northwest', '西北地区:甘肃'),
('16', 'Guangxi', 'Southern China', '华南地区:广西'),
('17', 'Hong Kong', 'Hong Kong,Macao and Taiwan', '港澳台地区:香港'),
('18', 'Guizhou', 'Southwest', '西南地区:贵州'),
('19', 'Liaoning', 'Northeast', '东北地区:辽宁'),
('20', 'Nei Mongol', 'North China', '华北地区:内蒙古'),
('21', 'Ningxia', 'Northwest', '西北地区:宁夏'),
('22', 'Beijing', 'North China', '华北地区:北京'),
('23', 'Shanghai', 'East China', '华东地区:上海'),
('24', 'Shanxi', 'Northwest', '西北地区:陕西'),
('25', 'Shandong', 'East China', '华东地区:山东'),
('26', 'Shaanxi', 'North China', '华北地区:山西'),
('27', 'Macao', 'Hong Kong,Macao and Taiwan', '港澳台地区:澳门'),
('28', 'Tianjin', 'North China', '华北地区:天津'),
('29', 'Yunnan', 'Southwest', '西南地区:云南'),
('30', 'Guangdong', 'Southern China', '华南地区:广东'),
('31', 'Hainan', 'Southern China', '华南地区:海南'),
('32', 'Sichuan', 'Southwest', '西南地区:四川'),
('33', 'Chongqin', 'Southwest', '西南地区:重庆'),
('34', 'Taiwan', 'Hong Kong,Macao and Taiwan', '港澳台地区:台湾');'''

# insert table `t_countrycode`
incountrycode = '''INSERT INTO `t_countrycode` (`CountryCode`, `EnCountry`, `CnCountry`, `Continent`) VALUES
('AF', 'Afghanistan', '阿富汗', 'Asia'),
('AG', 'Antigua and Barbuda', '安提瓜岛', 'America'),
('AI', 'Anguilla The Valley', '安圭拉岛', 'America'),
('AL', 'Albania', '阿尔巴尼亚', 'Europe'),
('AO', 'Angola', '安哥拉', 'Africa'),
('AR', 'Argentina', '阿根廷', 'America'),
('AT', 'Austria', '奥地利', 'Europe'),
('AU', 'Australia', '澳大利亚', 'Oceania'),
('BB', 'Barbados', '巴巴多斯岛', 'America'),
('BD', 'Bangladesh', '孟加拉国', 'Asia'),
('BE', 'Belgium', '比利时', 'Europe'),
('BG', 'Bulgaria', '保加利亚', 'Europe'),
('BI', 'Burundi', '布隆迪', 'Africa'),
('BJ', 'Benin', '贝宁', 'Africa'),
('BM', 'Bermuda', '百慕大群岛', 'America'),
('BN', 'Brunei Darussalam', '文莱', 'Asia'),
('BO', 'Bolivia', '玻利维亚', 'America'),
('BR', 'Brazil', '巴西', 'America'),
('BS', 'The Bahamas', '巴哈马', 'America'),
('BT', 'Bhutan', '不丹', 'Asia'),
('BW', 'Botswana', '博茨瓦纳', 'Africa'),
('BZ', 'Belize', '伯利兹', 'America'),
('CA', 'Canada', '加拿大', 'America'),
('CD', 'CONGO, Democratic Republic of (was Zaire)', '刚果民主共和国', 'Africa'),
('CF', 'Central African Republic', '中非', 'Africa'),
('CG', 'CONGO, Republic of', '刚果共和国', 'Africa'),
('CH', 'Switzerland', '瑞士', 'Europe'),
('CL', 'Chile', '智利', 'America'),
('CM', 'Cameroon', '喀麦隆', 'Africa'),
('CN', 'China', '中国', 'Asia'),
('CO', 'Colombia', '哥伦比亚', 'America'),
('CR', 'Costa Rica', '哥斯达黎加', 'America'),
('CU', 'Cuba', '古巴', 'America'),
('CY', 'Cyprus', '塞浦路斯', 'Europe'),
('DE', 'Germany', '德国', 'Europe'),
('DJ', 'Djibouti', '吉布提共和国', 'Africa'),
('DK', 'Denmark', '丹麦', 'Europe'),
('DO', 'Dominican Republic', '多米尼加', 'America'),
('DZ', 'Algeria', '阿尔及利亚', 'Africa'),
('EC', 'Ecuador', '厄瓜多尔', 'America'),
('EG', 'Egypt', '埃及', 'Africa'),
('EH', 'Western Sahara', '西撒哈拉', 'Africa'),
('ER', 'Eritrea', '厄立特里亚', 'Africa'),
('ES', 'Spain', '西班牙', 'Europe'),
('ET', 'Ethiopia', '埃塞俄比亚', 'Africa'),
('FI', 'Finland', '芬兰', 'Europe'),
('FR', 'France', '法国', 'Europe'),
('GA', 'Gabon', '加蓬', 'Africa'),
('GB', 'United Kingdom', '大不列颠联合王国', 'Europe'),
('GD', 'Grenada', '格林纳达', 'America'),
('GH', 'Ghana', '加纳', 'Africa'),
('GL', 'Greenland Nuuk (Godthab)', '格陵兰', 'America'),
('GM', 'The Gambia', '冈比亚', 'Africa'),
('GN', 'Guinea', '几内亚', 'Africa'),
('GP', 'Guadeloupe', '瓜德罗普岛', 'America'),
('GQ', 'Equatorial', '赤道几内亚', 'Africa'),
('GR', 'Greece', '希腊', 'Europe'),
('GT', 'Guatemala', '危地马拉', 'America'),
('GW', 'Guinea-Bissau', '几内亚比绍共和国', 'Africa'),
('GY', 'Guyana', '圭亚那', 'America'),
('HN', 'Honduras', '洪都拉斯', 'America'),
('HR', 'Croatia', '克罗地亚', 'Europe'),
('HT', 'Haiti', '海地', 'America'),
('HU', 'Hungary', '匈牙利', 'Europe'),
('ID', 'Indonesia', '印度尼西亚', 'Asia'),
('IE', 'Ireland', '爱尔兰', 'Europe'),
('IN', 'India', '印度', 'Asia'),
('IS', 'Iceland', '冰岛', 'Europe'),
('IT', 'Italy', '意大利', 'Europe'),
('JM', 'Jamaica', '牙买加', 'America'),
('JP', 'Japan', '日本', 'Asia'),
('KE', 'Kenya', '肯尼亚', 'Africa'),
('KH', 'Cambodia', '柬埔寨', 'Asia'),
('KI', 'Kiribati', '基里巴斯', 'Oceania'),
('KP', 'Democratic Peoples Republic of Korea', '朝鲜', 'Asia'),
('KR', 'KOREA, REPUBLIC OF', '韩国', 'Asia'),
('LA', 'LAO PEOPLES DEMOCRATIC REPUBLIC', '老挝', 'Asia'),
('LC', 'St. Lucia', '圣卢西亚岛', 'America'),
('LI', 'Liechtenstein', '列支敦士登', 'Europe'),
('LK', 'Sri Lanka', '斯里兰卡', 'Asia'),
('LR', 'Liberia', '利比里亚', 'Africa'),
('LS', 'Lesotho', '莱索托', 'Africa'),
('LU', 'Luxembourg', '卢森堡', 'Europe'),
('LY', 'Libya', '利比亚', 'Africa'),
('MA', 'Morocco', '摩洛哥', 'Africa'),
('MC', 'Monaco', '摩纳哥', 'Europe'),
('MG', 'Madagasca', '马达加斯加', 'Africa'),
('MK', 'Macedonia Skopje', '马其顿', 'Europe'),
('ML', 'Mali', '马里', 'Africa'),
('MN', 'Mongolia', '蒙古', 'Asia'),
('MQ', 'Martinique', '马提尼克岛', 'America'),
('MR', 'Mauritania', '毛里塔尼亚', 'Africa'),
('MS', 'Montserrat', '蒙特塞拉特岛', 'America'),
('MT', 'Malta', '马耳他', 'Europe'),
('MU', 'Mauritius', '毛里求斯', 'Africa'),
('MV', 'Maldives', '马尔代夫', 'Asia'),
('MW', 'Malawi', '马拉维', 'Africa'),
('MX', 'Mexico', '墨西哥', 'America'),
('MY', 'Malaysia', '马来西亚', 'Asia'),
('MZ', 'Mozambique', '莫桑比克', 'Africa'),
('NA', 'Namibia', '纳米比亚', 'Africa'),
('NE', 'Niger', '尼日尔', 'Africa'),
('NG', 'Nigeria', '尼日利亚', 'Africa'),
('NI', 'Nicaragua', '尼加拉瓜', 'America'),
('NL', 'Netherlands', '荷兰', 'Europe'),
('NO', 'Norway', '挪威', 'Europe'),
('NP', 'Nepal', '尼泊尔', 'Asia'),
('NR', 'Nauru', '瑙鲁', 'Oceania'),
('PA', 'Panama', '巴拿马', 'America'),
('PE', 'Peru', '秘鲁', 'America'),
('PH', 'Philippines', '菲律宾共和国', 'Asia'),
('PK', 'Pakistan', '巴基斯坦', 'Asia'),
('PL', 'Poland', '波兰', 'Europe'),
('PR', 'Puerto Rico', '波多黎各岛', 'America'),
('PS', 'Palestine', '巴勒斯坦', 'Asia'),
('PT', 'Portugal', '葡萄牙', 'Europe'),
('PY', 'Paraguay', '巴拉圭', 'America'),
('RE', 'Reunion', '留尼旺岛', 'Africa'),
('RO', 'Romania', '罗马尼亚', 'Europe'),
('RU', 'Russia', '俄罗斯', 'Europe'),
('RW', 'Rwanda', '卢旺达', 'Africa'),
('SC', 'Seychelles', '塞舌尔', 'Africa'),
('SD', 'Sudan', '苏丹', 'Africa'),
('SE', 'Sweden', '瑞典', 'Europe'),
('SG', 'Singapore', '新加坡', 'Asia'),
('SI', 'Slovenia Ljubljana', '斯洛文尼亚', 'Europe'),
('SK', 'Sikkim', '锡金', 'Asia'),
('SL', 'Sierra Leone', '塞拉里昂', 'Africa'),
('SM', 'San Marino', '圣马利诺', 'Europe'),
('SN', 'Senegal', '塞内加尔', 'Africa'),
('SO', 'Somalia', '索马里', 'Africa'),
('SR', 'Suriname', '苏里南', 'America'),
('ST', 'Sao Tome and Principe', '圣多美及普林西比民主共和国', 'Africa'),
('SV', 'El Salvador', '萨尔瓦多', 'America'),
('SZ', 'Swaziland', '斯威士兰', 'Africa'),
('TC', 'TURKS AND CAICOS ISLANDS', '特克斯群岛和凯科斯群岛', 'America'),
('TD', 'Chad', '乍得', 'Africa'),
('TG', 'Togo', '多哥', 'Africa'),
('TH', 'Thailand', '泰国', 'Asia'),
('TN', 'Tunisia', '突尼斯', 'Africa'),
('TO', 'Tonga', '汤加', 'Oceania'),
('TR', 'Turkey', '土耳其', 'Asia'),
('TT', 'Trinidad and Tobago', '特立尼达和多巴哥', 'America'),
('TZ', 'Tanzania', '坦桑尼亚', 'Africa'),
('UG', 'Uganda', '乌干达', 'Africa'),
('US', 'United States', '美国', 'America'),
('UY', 'Uruguay', '乌拉圭', 'America'),
('VC', 'SAINT VINCENT AND THE GRENADINES', '圣文森特岛', 'America'),
('VE', 'Venezuela', '委内瑞拉', 'America'),
('VG', 'VIRGIN ISLANDS (BRITISH)', '英属维尔京群岛', 'America'),
('VI', 'VIRGIN ISLANDS (U.S.)', '美属维尔京群岛', 'America'),
('VN', 'Socialist Republic of Vietnam', '越南', 'Asia'),
('VU', 'Vanuatu', '瓦努阿图', 'Oceania'),
('ZA', 'South Africa', '南非', 'Africa'),
('ZM', 'Zambia', '赞比亚', 'Africa'),
('ZW', 'Zimbabwe', '津巴布韦', 'Africa');'''

# creat access tables
def creatacctables(cursor):
    global gettables
    for (k,v) in  gettables.items():
        cursor.execute(v)
    
def insert_init(cursor):
    global infileseat
    global inareas
    global incountrycode

    count1 = cursor.execute('select * from t_fileseat')
    count2 = cursor.execute('select * from t_areas')
    count3 = cursor.execute('select * from t_countrycode')
    if(count1 <= 0):
        cursor.execute(infileseat)
    if(count2 <= 0):
        cursor.execute(inareas)
    if(count3 <= 0):
        cursor.execute(incountrycode)
    
# creat table t_alertlogs_[date],t_accesslogs_[date],pages_[date],visitors_[date] t_counturi_[date]
def creatlogstables(tdate):
    global alertlog
    global accesslog
    global pages
    global visitors
    global counturi
    global ddoslog
    global syslog
    global weboutlog
    conn = MySQLdb.connect(db=config['dbacc']['db'], user=config['dbacc']['user'], passwd=config['dbacc']['passwd'], charset='utf8')
    cursor = conn.cursor()
    
    sqlalert     = "CREATE TABLE IF NOT EXISTS `t_alertlogs_%s`" % tdate
    sqlaccess    = "CREATE TABLE IF NOT EXISTS `t_accesslogs_%s`" % tdate
    sqlpages     = "CREATE TABLE IF NOT EXISTS `pages_%s`" % tdate
    sqlvisitors  = "CREATE TABLE IF NOT EXISTS `visitors_%s`" % tdate
    sqlruleid    = "CREATE TABLE IF NOT EXISTS `t_ruleid_%s`" % tdate
    sqlsourceip  = "CREATE TABLE IF NOT EXISTS `t_sourceip_%s`" % tdate
    sqlcounturi  = "CREATE TABLE IF NOT EXISTS `t_counturi_%s`" % tdate
    sqlcountsety = "CREATE TABLE IF NOT EXISTS `t_countsety_%s`" % tdate
    sqlddoslog   = "CREATE TABLE IF NOT EXISTS `t_ddoslogs_%s`" % tdate
    sqlsyslog    = "CREATE TABLE IF NOT EXISTS `t_syslogs_%s`" % tdate
    sqlweboutlog = "CREATE TABLE IF NOT EXISTS `t_weboutlogs_%s`" % tdate

    sqlpages     += pages
    sqlvisitors  += visitors
    sqlalert     += alertlog
    sqlaccess    += accesslog
    sqlruleid    += ruleid
    sqlsourceip  += sourceip
    sqlcounturi  += counturi
    sqlcountsety += countsety
    sqlddoslog   += ddoslog
    sqlsyslog    += syslog
    sqlweboutlog += weboutlog
    cursor.execute(sqlaccess)
    cursor.execute(sqlalert)
    cursor.execute(sqlpages)
    cursor.execute(sqlvisitors)
    cursor.execute(sqlruleid)
    cursor.execute(sqlsourceip)
    cursor.execute(sqlcounturi)
    cursor.execute(sqlcountsety)
    cursor.execute(sqlddoslog)
    cursor.execute(sqlsyslog)
    cursor.execute(sqlweboutlog)

    creatacctables(cursor)
    insert_init(cursor)
    conn.commit()
    cursor.close()
    conn.close()

'''
def creatwaftables(tdate):
    global waftables
    global inddosset
    conn = MySQLdb.connect(db=config['db']['db'], user=config['db']['user'], passwd=config['db']['passwd'], charset='utf8')
    cursor = conn.cursor()
    
    for (k,v) in  waftables.items():
        cursor.execute(v)

    count1 = cursor.execute('select * from t_ddosset')
    #count2 = cursor.execute('select * from t_advance')
    if(count1 <= 0):
        cursor.execute(inddosset)
    #if(count2 <= 0):
    #    cursor.execute(inadvance)

    conn.commit()
    cursor.close()
    conn.close()
'''

if __name__ == '__main__':
    tdate = time.strftime("%Y%m", time.localtime())
    creatlogstables(tdate)
    #creatwaftables(tdate)
