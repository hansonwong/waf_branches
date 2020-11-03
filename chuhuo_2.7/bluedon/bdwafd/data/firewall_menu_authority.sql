-- MySQL dump 10.13  Distrib 5.6.30, for Linux (x86_64)
--
-- Host: localhost    Database: db_firewall
-- ------------------------------------------------------
-- Server version	5.6.30

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `m_tbnavtree`
--
use db_firewall;
DROP TABLE IF EXISTS `m_tbnavtree`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbnavtree` (
  `iNavId` bigint(20) NOT NULL AUTO_INCREMENT,
  `iParentId` bigint(20) NOT NULL,
  `sName` varchar(50) NOT NULL,
  `iSort` smallint(8) NOT NULL,
  `sUrl` varchar(50) DEFAULT NULL,
  `sRel` varchar(100) DEFAULT NULL,
  `sTarget` varchar(100) DEFAULT NULL,
  `sIcon` varchar(200) DEFAULT NULL,
  `sClass` varchar(100) DEFAULT NULL,
  `sClass2` varchar(100) DEFAULT NULL,
  `iLevel` int(10) NOT NULL,
  `bVisible` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`iNavId`)
) ENGINE=MyISAM AUTO_INCREMENT=205 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_tbnavtree`
--

LOCK TABLES `m_tbnavtree` WRITE;
/*!40000 ALTER TABLE `m_tbnavtree` DISABLE KEYS */;
INSERT INTO `m_tbnavtree` VALUES (1,0,'首页',1,'System/Index','home','right','home','menu_icon home','menu_s menu_small_icon',1,1),(2,0,'系统',2,'',NULL,'','xt','menu_icon xt','menu_s menu_small_icon',1,1),(3,2,'管理员帐号',0,'Account/Index','jjgl','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(4,2,'系统配置',3,'Systemsetting/Index','jjsbgl','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(5,2,'系统维护',4,'Systemmaintenance/Index','pcgl','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(6,2,'高可用性',5,'Ha/Index','sbzt','','gkyx','menu_icon gkyx','menu_s menu_small_icon',2,1),(9,0,'用户管理',9,NULL,NULL,'','yhgl','menu_icon smbs','',2,1),(10,9,'组/用户',0,'Users/GroupsUsers','basic','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(11,9,'用户认证',0,'Users/UserAuthentication','aqgf','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(12,0,'网络设置',5,'','aqyf','right','wlsz','menu_sicon menu_small_icon','menu_s menu_small_icon',1,1),(13,12,'网口配置',0,'Network/NetPort','stsx','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(14,12,'虚拟线',2,'Network/VirtualLine','fwsx','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(15,12,'桥设备',2,'Network/BridgeDevice','idsx','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(16,12,'拨号设备',2,'Network/DialDevice','sssx','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(17,12,'端口聚合',2,'Network/PortAggregation','gfbs','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(18,12,'VLAN设备',2,'Network/VlanDevice','zdysy','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(19,105,'静态路由',2,'Network/StaticRoute',NULL,'right','','menu_icon wlxws','',2,1),(20,105,'策略路由',2,'Network/StrategyRoute','bjgl','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(21,105,'ISP路由',2,'Network/IspRoute','xsgl','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(22,105,'动态路由',2,'Network/DynamicRoute','drxs','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(23,12,'DHCP',2,'Network/DHCP','sbzt','right','','menu_icon sbzt','',2,1),(24,12,'DNS设置',2,'Network/DnsSetting',NULL,'right','','menu_icon cxtj','menu_s menu_small_icon',1,1),(25,0,'对象定义',6,'','sblx','','dxdy','menu_sicon menu_small_icon',NULL,2,1),(26,25,'IP/IP组',0,'Objectdefine/addressManagement','sbxh','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(27,25,'ISP地址',0,'Objectdefine/IspAddress','cssz','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(29,25,'服务/组',0,'Objectdefine/Service','yhsz','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(30,25,'URL类型组',0,'Objectdefine/UrlType','rzgl','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(31,25,'文件类型组',0,'Objectdefine/FileType','gjgl','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(34,25,'时间计划',0,'Objectdefine/TimePlan',NULL,'right','','menu_icon wlxwj','',2,1),(35,25,'自定义IPS规则库',0,'Objectdefine/IpsRuleLib','bggl','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(36,25,'WEB应用防护规则库',0,'Objectdefine/SafeRuleLib','bgmb','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(37,25,'自定义应用',0,'Objectdefine/CustomApp','home','right','','menu_icon xtzy','',2,0),(38,0,'防火墙',8,'','wdkt','','fhq','menu_icon clgl','menu_s menu_small_icon',1,1),(39,38,'安全策略',0,'Searitystrate/Index','home_bak','right','','menu_icon xtzy','',2,1),(40,38,'NAT',0,'Nat/Index','','right','','menu_icon scjc','',2,1),(41,38,'连接数控制',0,'Connectnum/Index','home','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(42,38,'DOS/DDOS防护',0,'Ddos/Index','yxsy','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(43,78,'URL过滤',0,NULL,'lssy','right',NULL,'menu_sicon menu_small_icon',NULL,2,1),(45,78,'入侵防护',0,'Ips/Index',NULL,'right',NULL,NULL,NULL,2,1),(46,0,'流量管理',12,NULL,NULL,NULL,'llgl',NULL,'menu_s menu_small_icon',1,1),(47,46,'虚拟线路',0,'Virtualline/Index',NULL,'right',NULL,NULL,NULL,2,1),(48,46,'通道配置',0,'Socketset/Index',NULL,'right',NULL,NULL,NULL,2,1),(49,78,'web应用防护',0,'Webapp/Index',NULL,'right','yyfh',NULL,'menu_s menu_small_icon',2,1),(50,78,'病毒防护',0,NULL,NULL,'right','bdfh',NULL,'menu_s menu_small_icon',2,1),(51,78,'信息泄漏防护',0,'Filefilter/ProtectedIndex',NULL,NULL,'xxxl',NULL,'menu_s menu_small_icon',2,1),(52,51,'关键词过滤',0,'Keywordfilter/Index',NULL,'right',NULL,NULL,NULL,2,1),(53,51,'文件过滤',0,'Filefilter/Index',NULL,'right',NULL,NULL,NULL,2,1),(54,0,'智能防护',14,NULL,NULL,NULL,'znfh',NULL,'menu_s menu_small_icon',1,1),(55,54,'策略自动演进',0,'Autorqrule/Index',NULL,'right',NULL,NULL,NULL,2,1),(56,54,'蜜罐',0,'Honeypot/Index',NULL,'right',NULL,NULL,NULL,2,1),(57,54,'反向拍照',0,'Revcamera/Index',NULL,'right',NULL,NULL,NULL,2,1),(58,54,'防扫描',0,'Revscan/Index',NULL,'right',NULL,NULL,NULL,2,1),(59,38,'联动',15,'Linkage/Index',NULL,NULL,'ld',NULL,'menu_s menu_small_icon',1,1),(61,0,'报表日志',16,NULL,NULL,NULL,'bbrz',NULL,'menu_s menu_small_icon',1,1),(62,61,'日志配置',0,'Logconf/Index',NULL,'right',NULL,NULL,NULL,2,1),(63,61,'系统日志',0,'Syslog/Index',NULL,'right',NULL,NULL,NULL,2,1),(64,61,'防火墙日志',0,'Fwlog/IndexFw',NULL,'right',NULL,NULL,NULL,2,1),(65,61,'入侵防御日志',0,'Fwlog/IndexIps',NULL,'right',NULL,NULL,NULL,2,1),(66,61,'web应用防护日志',0,'Protectlog/IndexWeb',NULL,'right',NULL,NULL,NULL,2,1),(67,61,'病毒防护日志',0,'Protectlog/IndexCode',NULL,'right',NULL,NULL,NULL,2,1),(68,61,'信息泄漏防护日志',0,'Protectlog/IndexInfo',NULL,'right',NULL,NULL,NULL,2,1),(69,61,'DDOS防护日志',0,'Ddoslog/Index',NULL,'right',NULL,NULL,NULL,2,1),(70,61,'应用管控日志',0,'Applylog/Index',NULL,'right',NULL,NULL,NULL,2,1),(71,61,'url访问日志',0,'Urllog/Index',NULL,'right',NULL,NULL,NULL,2,1),(72,61,'日志库',0,'Loglab/Index',NULL,'right',NULL,NULL,NULL,2,1),(73,61,'报表统计',0,'Report/Index',NULL,'right',NULL,NULL,NULL,2,1),(74,0,'配置向导',17,'Confguide/Index',NULL,NULL,'pzxd',NULL,'menu_s menu_small_icon',1,1),(75,2,'角色权限',0,'Account/Permission',NULL,'right',NULL,NULL,NULL,2,1),(76,12,'端口镜像',0,'Network/PortMirror',NULL,'right',NULL,NULL,NULL,2,1),(77,38,'IP-MAC绑定配置',2,'Ipmac/index',NULL,'right',NULL,NULL,NULL,2,1),(78,0,'安全防护',9,NULL,NULL,'right','aqfh',NULL,NULL,1,1),(79,61,'用户认证日志',0,'Userslog/Index',NULL,'right',NULL,NULL,NULL,2,1),(80,61,'网中网检测日志',0,'Sharelog/Index',NULL,'right',NULL,NULL,NULL,2,1),(81,97,'SSL VPN',0,'',NULL,'right','',NULL,NULL,2,1),(82,81,'基本配置',0,'Sslvpn/Setting',NULL,'right',NULL,NULL,NULL,3,1),(83,81,'服务管理',0,'Sslvpn/Csservice',NULL,'right',NULL,NULL,NULL,3,0),(84,81,'角色管理',0,'Sslvpn/Role',NULL,'right',NULL,NULL,NULL,3,0),(85,81,'用户管理',0,'Sslvpn/Usermag',NULL,'right',NULL,NULL,NULL,3,0),(86,97,'IPSEC VPN',0,NULL,NULL,NULL,'',NULL,NULL,2,1),(87,97,'L2TP VPN',0,NULL,NULL,'right',NULL,NULL,NULL,2,1),(88,86,'本地子网',0,'Ipsec/Netindex',NULL,'right',NULL,NULL,NULL,3,1),(89,86,'网口配置',0,'Ipsec/Netport',NULL,'right',NULL,NULL,NULL,3,1),(92,86,'算法列表配置',0,'Ipsec/Algorithmset',NULL,'right',NULL,NULL,NULL,3,1),(93,86,'分支对接',0,'Ipsecbranch/Index',NULL,'right',NULL,NULL,'',3,1),(94,12,'IPV6隧道配置',3,'Ipvtunnelset/Index',NULL,NULL,NULL,NULL,NULL,1,1),(98,38,'会话管理',0,NULL,NULL,'right',NULL,NULL,NULL,2,1),(99,98,'会话控制',0,'Fwsession/Control',NULL,'right',NULL,NULL,NULL,3,1),(97,0,'虚拟专网',10,NULL,NULL,'right','vpn',NULL,NULL,1,1),(100,98,'连接排行榜',0,'Fwsession/Connetrank',NULL,'right',NULL,NULL,NULL,3,1),(101,98,'会话状态',0,'Fwsession/Sessionstatus',NULL,'right',NULL,NULL,NULL,3,1),(103,12,'NAT64配置',3,'Natsetting/Index',NULL,'right',NULL,NULL,NULL,1,1),(104,97,'NAT 穿越',0,NULL,NULL,NULL,'',NULL,NULL,2,1),(105,0,'路由配置',5,NULL,NULL,'right','lypz',NULL,NULL,1,1),(106,105,'ECMP',0,'Ecmp/Index',NULL,'right',NULL,NULL,NULL,2,1),(107,61,'IpsecVPN日志',0,'Ipseclog/Index',NULL,'right',NULL,NULL,NULL,2,1),(108,97,'GRE隧道',0,'Gre/Index',NULL,'right',NULL,NULL,NULL,2,1),(109,104,'中心节点',0,'Ntn/Center',NULL,'right',NULL,NULL,NULL,2,1),(110,104,'边缘节点',0,'Ntn/Edge',NULL,'right',NULL,NULL,NULL,2,1),(133,132,'入侵防护识别库',0,'Ipsreclib/Index',NULL,NULL,NULL,NULL,NULL,2,1),(134,132,'WEB应用防护识别库',0,'Webreclib/Index',NULL,NULL,NULL,NULL,NULL,2,1),(135,132,'URL分类库',0,'Urlclasslib/Index',NULL,NULL,NULL,NULL,NULL,2,1),(136,132,'规则库升级配置',0,'Rulelibupdate/Index',NULL,NULL,NULL,NULL,NULL,2,1),(137,0,'规则库升级日志',29,'','rzgl',NULL,'sjrz','menu_icon rzgl','menu_s menu_small_icon',1,1),(144,0,'生产页面-生产部',31,'Productlicense/Index/type/create','smzgl',NULL,'scb','menu_icon smzgl',NULL,1,0),(143,0,'产品许可',30,'Productlicense/show','fqrj',NULL,'cpxk','menu_icon fqrj','',1,0),(142,137,'病毒库升级日志',0,'Viruslibupdate/Index',NULL,NULL,NULL,NULL,NULL,2,1),(138,137,'入侵防护规则库',0,'Ipsrulelibupdate/Index',NULL,NULL,NULL,NULL,NULL,2,1),(139,137,'WEB应用防护规则库',0,'Webrulelibupdate/Index',NULL,NULL,NULL,NULL,NULL,2,1),(140,137,'URL规则库升级日志',0,'Urlrulelibupdate/Index',NULL,NULL,NULL,NULL,NULL,2,1),(141,137,'应用规则库升级日志',0,'Apprulelibupdate/Index',NULL,NULL,NULL,NULL,NULL,2,1),(145,38,'虚拟防火墙',32,'Virtualfw/Index','','right','','','',1,1),(146,0,'日志任务',26,'Exportlog/Index',NULL,'right','rzrw',NULL,NULL,1,1),(147,0,'上网行为审计',27,'',NULL,'right','swxw','menu_icon  yysj',NULL,2,1),(148,147,'网络邮件',0,'Webmail/Index',NULL,'right',NULL,NULL,NULL,2,1),(149,147,'博客',0,'Blog/Index',NULL,'right',NULL,NULL,NULL,2,1),(150,147,'搜索引擎',0,'Search/Index',NULL,'right',NULL,NULL,NULL,2,1),(151,147,'微博',0,'Weibo/Index',NULL,'right',NULL,NULL,NULL,2,1),(152,147,'网盘',0,'Netstore/Index',NULL,'right',NULL,NULL,NULL,2,1),(153,147,'网络论坛',0,'Bbs/Index',NULL,'right',NULL,NULL,NULL,2,1),(154,147,'网络购物',0,'Shopping/Index',NULL,'right',NULL,NULL,NULL,2,1),(155,147,'视频',0,'Video/Index',NULL,'right',NULL,NULL,NULL,2,1),(156,147,'网页浏览',0,'Http/Index','','right','','','',2,1),(157,147,'ftp',0,'Ftp/Index','','right','','','',2,1),(158,147,'数据库',0,'Database/Index','','right','','','',2,0),(159,147,'翻墙软件',0,'Proxy/Index',NULL,'right',NULL,NULL,NULL,2,1),(160,147,'网络游戏',0,'Game/Index',NULL,'right',NULL,NULL,NULL,2,1),(161,147,'木马事件',0,'Trojan/Index',NULL,'right',NULL,NULL,NULL,2,1),(162,147,'Telnet',0,'Telnet/Index',NULL,'right',NULL,NULL,NULL,2,1),(163,147,'QQ通信',0,'Qq/Index',NULL,'right',NULL,NULL,NULL,2,1),(164,147,'P2P软件',0,'P2p/Index',NULL,'right',NULL,NULL,NULL,2,1),(165,147,'股票软件',0,'Stock/Index',NULL,'right',NULL,NULL,NULL,2,1),(166,147,'DNS',0,'Dns/Index',NULL,'right',NULL,NULL,NULL,2,0),(167,147,'NetBIOS',0,'Netbios/Index',NULL,'right',NULL,NULL,NULL,2,1),(168,147,'NFS',0,'Nfs/Index',NULL,'right',NULL,NULL,NULL,2,1),(169,147,'境外审计',0,NULL,NULL,'right','jwsj','menu_icon  jwsj',NULL,2,1),(170,169,'ftp',10,'Ftp/Overseas','','right','','','',2,1),(171,169,'数据库',11,'Database/Overseas','','right','','','',2,0),(172,169,'网络邮件',0,'Webmail/Overseas',NULL,'right',NULL,NULL,NULL,2,1),(173,169,'博客',0,'Blog/Overseas',NULL,'right',NULL,NULL,NULL,2,1),(174,169,'搜索引擎',0,'Search/Overseas',NULL,'right',NULL,NULL,NULL,2,1),(175,169,'微博',0,'Weibo/Overseas',NULL,'right',NULL,NULL,NULL,2,1),(176,169,'网盘',0,'Netstore/Overseas',NULL,'right',NULL,NULL,NULL,2,1),(177,169,'网络论坛',0,'Bbs/Overseas',NULL,'right',NULL,NULL,NULL,2,1),(178,169,'网络购物',0,'Shopping/Overseas',NULL,'right',NULL,NULL,NULL,2,1),(179,169,'视频',0,'Video/Overseas',NULL,'right',NULL,NULL,NULL,2,1),(180,169,'网页浏览',9,'Http/Overseas',NULL,'right',NULL,NULL,NULL,2,1),(181,169,'翻墙软件',12,'Proxy/Overseas',NULL,'right',NULL,NULL,NULL,2,1),(182,169,'网络游戏',13,'Game/Overseas',NULL,'right',NULL,NULL,NULL,2,1),(183,169,'木马事件',14,'Trojan/Overseas',NULL,'right',NULL,NULL,NULL,2,1),(184,169,'Telnet',15,'Telnet/Overseas',NULL,'right',NULL,NULL,NULL,2,1),(185,169,'QQ通信',16,'Qq/Overseas',NULL,'right',NULL,NULL,NULL,2,1),(186,169,'P2P软件',17,'P2p/Overseas',NULL,'right',NULL,NULL,NULL,2,1),(187,169,'股票软件',18,'Stock/Overseas',NULL,'right',NULL,NULL,NULL,2,1),(188,169,'DNS',19,'Dns/Overseas',NULL,'right',NULL,NULL,NULL,2,0),(189,169,'NetBIOS',20,'Netbios/Overseas',NULL,'right',NULL,NULL,NULL,2,1),(190,169,'NFS',0,'Nfs/Overseas',NULL,'right',NULL,NULL,NULL,2,1),(191,87,'基本配置',0,'Bdl2tpvpn/Setting',NULL,'right',NULL,NULL,NULL,3,1),(192,87,'监控管理',0,'Bdl2tpvpn/Monitor',NULL,'right',NULL,NULL,NULL,3,1),(193,87,'服务管理',0,'Bdl2tpvpn/Service',NULL,'right',NULL,NULL,NULL,3,1),(194,87,'用户配置',0,'Bdl2tpvpn/User',NULL,'right',NULL,NULL,NULL,3,1),(195,87,'虚拟池IP',0,'Ipsec/VirtualNet',NULL,'right',NULL,NULL,NULL,3,1),(196,87,'时间配置',0,'Ipsec/Timeset',NULL,'right',NULL,NULL,NULL,3,0),(197,81,'服务管理',0,'Bdsslvpn/Service',NULL,'right',NULL,NULL,NULL,3,1),(198,81,'用户配置',0,'Bdsslvpn/User',NULL,'right',NULL,NULL,NULL,3,1),(199,86,'IPSEC监控管理',0,'Ipsec/Monitor',NULL,'right',NULL,NULL,NULL,3,1),(200,43,'URL过滤策略',2,'Urlfilter/Index',NULL,'right',NULL,NULL,NULL,1,1),(201,43,'URL黑名单',2,'Urlsecurity/Black',NULL,'right',NULL,NULL,NULL,1,1),(202,43,'URL白名单',2,'Urlsecurity/White',NULL,'right',NULL,NULL,NULL,1,1),(203,50,'基本配置',2,'Maliciouscode/EvilProtectedSet',NULL,'right',NULL,NULL,NULL,1,1),(204,50,' 防病毒策略设置',2,'Maliciouscode/EvilIndex',NULL,'right',NULL,NULL,NULL,1,1);
/*!40000 ALTER TABLE `m_tbnavtree` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `m_tbrolenavtree`
--

DROP TABLE IF EXISTS `m_tbrolenavtree`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `m_tbrolenavtree` (
  `iId` int(11) NOT NULL AUTO_INCREMENT,
  `iRoleId` bigint(20) NOT NULL,
  `iNavId` bigint(20) NOT NULL,
  PRIMARY KEY (`iId`)
) ENGINE=MyISAM AUTO_INCREMENT=2383 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `m_tbrolenavtree`
--

LOCK TABLES `m_tbrolenavtree` WRITE;
/*!40000 ALTER TABLE `m_tbrolenavtree` DISABLE KEYS */;
INSERT INTO `m_tbrolenavtree` VALUES (2382,2,107),(2381,2,80),(2380,2,79),(2379,2,73),(2378,2,72),(2377,2,71),(2376,2,70),(2375,2,69),(2374,2,68),(2373,2,67),(2372,2,66),(2371,2,65),(2370,2,64),(2366,2,58),(2365,2,57),(2364,2,56),(2363,2,55),(2362,2,54),(2361,2,48),(2360,2,47),(2359,2,46),(2358,2,108),(2357,2,110),(2356,2,109),(2355,2,104),(2354,2,195),(2353,2,194),(2352,2,193),(2351,2,192),(2350,2,191),(2349,2,87),(2348,2,199),(2347,2,93),(2346,2,92),(2345,2,89),(2344,2,88),(2343,2,86),(2342,2,198),(2341,2,197),(2340,2,82),(2339,2,81),(2338,2,97),(2337,2,53),(2336,2,52),(2335,2,51),(2334,2,204),(2333,2,203),(2332,2,50),(2331,2,49),(2330,2,45),(2329,2,202),(2328,2,201),(2327,2,200),(2326,2,43),(2325,2,78),(2324,2,11),(2323,2,10),(2322,2,9),(2321,2,145),(2320,2,59),(2319,2,77),(2318,2,101),(2317,2,100),(2316,2,99),(2315,2,98),(2314,2,42),(2313,2,41),(2312,2,40),(2311,2,39),(2310,2,38),(2309,2,36),(2308,2,35),(2307,2,34),(2306,2,31),(2305,2,30),(2304,2,29),(2303,2,27),(2302,2,26),(2301,2,25),(2300,2,22),(2299,2,21),(2298,2,20),(2297,2,19),(2296,2,106),(2295,2,105),(2294,2,6),(2293,2,5),(2292,2,4),(2291,2,3),(2290,2,2),(2272,1,11),(2271,1,10),(2270,1,9),(2269,1,103),(2268,1,94),(2267,1,24),(2369,2,63),(2368,2,62),(2367,2,61),(2289,3,146),(2288,3,107),(2287,3,80),(2286,3,79),(2285,3,73),(2284,3,72),(2283,3,71),(2282,3,70),(2281,3,69),(2280,3,68),(2279,3,67),(2278,3,66),(2277,3,65),(2276,3,64),(2275,3,63),(2274,3,62),(2273,3,61),(2266,1,23),(2265,1,18),(2264,1,17),(2263,1,16),(2262,1,15),(2261,1,14),(2260,1,76),(2259,1,13),(2258,1,12),(2257,1,6),(2256,1,5),(2255,1,4),(2254,1,3),(2253,1,2);
/*!40000 ALTER TABLE `m_tbrolenavtree` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-03-12 16:10:45
