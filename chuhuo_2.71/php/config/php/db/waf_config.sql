-- MySQL dump 10.13  Distrib 5.6.30, for Linux (x86_64)
--
-- Host: localhost    Database: waf
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
-- Table structure for table `config`
--

DROP TABLE IF EXISTS `config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `config` (
  `symbol` char(255) NOT NULL,
  `desc` char(255) DEFAULT NULL,
  `field_desc` text,
  `json` text,
  PRIMARY KEY (`symbol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `config`
--

LOCK TABLES `config` WRITE;
/*!40000 ALTER TABLE `config` DISABLE KEYS */;
INSERT INTO `config` VALUES ('BaseConfig','安全管理 - 配置管理 - 基本参数设置','','{\"wafengine\":\"DetectionOnly\",\"defaultaction\":\"deny\",\"ports\":\"8|8|77\"}'),('ByPass','系统管理 - 网络配置 - Bypass设置','','{\"enable\":\"1\"}'),('CcSet','安全管理 -DDos防护 -CC防护设置','','{\"ccEnable\":\"0\",\"brouteEnable\":\"0\",\"ccPeriod\":\"\",\"broutePeriod\":\"\",\"ccTimes\":\"\",\"brouteTimes\":\"\",\"ccBlockTime\":\"\",\"brouteBlockTime\":\"\",\"brouteUris\":\"aaa;bbb;ccc\"}'),('DDosSet','安全管理 -DDos防护 -DDos防护设置','','{\"bankWidth\":\"1024\",\"totalPacket\":\"10000\",\"perPacket\":\"10000\",\"tcpPacket\":\"10000\",\"perTcpPacket\":\"10000\",\"synPacket\":\"10000\",\"perSynPacket\":\"10000\",\"ackPacket\":\"10000\",\"perAckPacket\":\"10000\",\"otherTcp\":\"10000\",\"perOtherTcp\":\"10000\",\"udpPacket\":\"10000\",\"perUdpPacket\":\"10000\",\"icmpPacket\":\"10000\",\"perIcmpPacket\":\"10000\",\"ddosEnable\":\"0\",\"udpEnable\":\"0\",\"icmpEnable\":\"0\"}'),('DiskClear','系统-系统维护 -磁盘清理','','{\"enable\":\"1\",\"limit\":\"\"}'),('FileExtension','安全管理 - 高级设置 - 文件扩展名过滤','','{\"extension\":{\"php\":\"php\",\"class\":\"class\",\"java\":\"java\",\"py\":\"py\",\"pyc\":\"pyc\",\"jpg\":\"jpg\",\"sfdsf\":\"sfdsf\",\"abcd\":\"abcd\"},\"extensionHidden\":\"\"}'),('FileExtensionForConfigList','安全管理 - 高级设置 - 文件扩展名过滤','','{\"extension\":\"[\\r\\n  \\\"php\\\",\\r\\n  \\\"class\\\",\\r\\n  \\\"java\\\",\\r\\n  \\\"py\\\",\\r\\n  \\\"pyc\\\",\\r\\n  \\\"jpg\\\",\\r\\n  \\\"ddsf\\\",\\r\\n  \\\"sfdsf\\\",\\r\\n  \\\"sdsss\\\",\\r\\n  \\\"abcd\\\"\\r\\n]\",\"extensionHidden\":\"\"}'),('Filter','安全管理-高级设置-HTTP请求动作过滤','','{\"extension\":[],\"extensionHidden\":\"\"}'),('HostLinkProtection','安全管理 - 高级设置 - 防盗链设置','','{\"file_type\":{\"raw\":\"raw\",\"tif\":\"tif\",\"fpx\":\"fpx\",\"svg\":\"svg\",\"psd\":\"psd\",\"ai\":\"ai\"}}'),('HttpContentType','安全管理-高级设置-HTTP请求内容过滤','','{\"extension\":[],\"extensionHidden\":\"\"}'),('HttpHeader','安全管理 - 高级设置 - HTTP头字段设置','','{\"extension\":[],\"extensionHidden\":\"\"}'),('IntelligentTrojanHorseSet','安全管理 - 高级设置 - 智能木马检测','','{\"status\":\"0\",\"maxFileSize\":\"8\",\"updateTime\":1522315599,\"interceptedFileSuffix\":\"[\\r\\n  \\\"py\\\",\\r\\n  \\\"php\\\",\\r\\n  \\\"xls\\\",\\r\\n  \\\"word\\\",\\r\\n  \\\"pdf\\\",\\r\\n  \\\"ppt\\\"\\r\\n]\"}'),('KeyWordAlert','关键字告警','status:是否开启，0-关闭，1-开启<br>\r\nurls	需要防护的url，留空则所有URL，多个则用‘|’分开,如 “/test|/test2”<br>\r\nexts:需要防护的文件扩展名，留空则为所有文件，多种类型则用‘|’隔开，如 “jgp|tar”<br>\r\nwords:敏感词，多个敏感词用‘|’隔开，如”法轮功|赌博”<br>\r\ncontent_size:需要处理的最大文件大小，超过这个阀值，则跳过处理<br>\r\nis_block:是否阻断，1-阻断，0-不阻断，默认0<br>\r\nalert_setting:告警设置，json格式，interval 邮件发送间隔（单位秒）\r\n{\"type\":\"email\",\"interval\":3600,\"email\":{\"receiver\":\"test@126.com\"}}<br>','{\"max_file_size\":\"\",\"urls\":\"[]\",\"exts\":\"[\\r\\n  \\\"jpg\\\",\\r\\n  \\\"png\\\",\\r\\n  \\\"docx\\\",\\r\\n  \\\"txt\\\",\\r\\n  \\\"tar\\\",\\r\\n  \\\"tar.gz\\\",\\r\\n  \\\"py\\\",\\r\\n  \\\"php\\\"\\r\\n]\",\"words\":\"[]\",\"alert_config\":\"\",\"status\":\"1\",\"is_block\":null}'),('MailAlert','系统 - 系统配置 - 报警设置','','{\"status\":\"0\",\"interval\":\"4\",\"phoneStatus\":\"0\",\"now\":\"\",\"maxValue\":\"\",\"cycle\":\"\",\"phoneCycle\":\"\"}'),('MailSet','系统 - 系统配置 - 通知配置','','{\"openMail\":\"1\",\"openPhone\":\"1\",\"smtpPort\":\"224\",\"sender\":\"abc@bluedon.com\",\"userName\":\"\",\"password\":\"www\",\"smtpServer\":\"bluedon.com\",\"receiver\":\"cdn@ccc.cn\",\"receiverPhone\":\"13800138000\"}'),('OcrSet','安全管理 - 高级设置 - OCR拦截','','{\"status\":\"0\",\"website_id\":\"\",\"words\":\"[\\r\\n  \\\"zvegew\\\",\\r\\n  \\\"ewrtuyog\\\",\\r\\n  \\\"cxv,mxc\\\"\\r\\n]\",\"update_time\":\"\",\"urls\":\"[\\r\\n  \\\"a\\\",\\r\\n  \\\"c\\\",\\r\\n  \\\"y\\\"\\r\\n]\",\"exts\":\"[\\r\\n  \\\"N\\\",\\r\\n  \\\"asfj\\\",\\r\\n  \\\"nvlqr\\\"\\r\\n]\"}'),('OutLinkSet','安全管理 -非法外联 -非法外联设置','','{\"enable\":\"1\",\"dports\":\"3|8888\"}'),('ProtocolVersion','安全管理-高级设置-HTTP协议版本过滤','','{\"extension\":{\"1\":\"1\",\"2\":\"2\"},\"extensionHidden\":\"\"}'),('SelfStudyResult','安全管理 - 自学习 - 自学习结果','','{\"uri_max\":\"1\",\"arg_name_max\":\"2\",\"arg_content_max\":\"3\",\"arg_count_max\":\"4\",\"cookie_max\":\"5\",\"cookie_name_max\":\"6\",\"cookie_content_max\":\"7\",\"cookie_count_max\":\"8\"}'),('SelfStudySet','安全管理 -自学习-自学习设置','','{\"is_ip_black\":\"\",\"is_domain_black\":\"\",\"is_use\":\"1\",\"is_ip_white\":\"1\",\"is_use_result\":\"0\"}'),('SensitiveWord','安全管理 - 高级设置 - 敏感词过滤设置','','{\"enable\":\"1\",\"words\":\"[\\r\\n  \\\"ppp\\\",\\r\\n  \\\"llll\\\"\\r\\n]\"}'),('ServerHeaderHide','安全管理 - 高级设置 - 服务器信息隐藏','','{\"list\":{\"X-Powered-By\":\"X-Powered-By\"}}'),('SmartBlock','安全管理 -DDos防护 -智能阻断设置','','{\"enable\":\"1\",\"cycle\":300,\"invade_count\":\"11\",\"standard_block_time\":\"600\"}'),('SpiderDefend','安全管理 - 高级设置 - 爬虫防护设置','','{\"list\":{\"Googlebot|Adsbot\":\"Googlebot|Adsbot\",\"baiduspider\":\"baiduspider\",\"Yahoo!\":\"Yahoo!\",\"iaskspider\":\"iaskspider\",\"YodaoBot\":\"YodaoBot\",\"msnbot\":\"msnbot\",\"bingbot\":\"bingbot\",\"Sosospider|Sosoblogspider|Sosoimagespider\":\"Sosospider|Sosoblogspider|Sosoimagespider\",\"360Spider\":\"360Spider\",\"ia_archiver\":\"ia_archiver\",\"lanshanbot\":\"lanshanbot\",\"Adminrtspider\":\"Adminrtspider\",\"HuaweiSymantecSpider\":\"HuaweiSymantecSpider\",\"MJ12bot\":\"MJ12bot\",\"YandexBot\":\"YandexBot\",\"Yeti\":\"Yeti\",\"DoCoMo\":\"DoCoMo\",\"HTTrack\":\"HTTrack\",\"checkbox\":\"checkbox\",\"Datapark\":\"Datapark\",\"JSpider\":\"JSpider\",\"python\":\"python\",\"curl\":\"curl\",\"wget\":\"wget\"}}'),('SysLoginConfig','登录配置','max_error:登录尝试次数限制<br>\r\nlock_time:登录错误锁定时间(分钟)<br>\r\nmax_timeout:登录超时时间(分钟)<br>\r\nsystem_default_language:系统默认语言<br>','{\"single_user_login_count_limit\":\"10\",\"max_error\":\"10\",\"lock_time\":\"3\",\"max_timeout\":\"1440\",\"system_default_language\":\"zh-CN\"}'),('WafSsh','系统 - 系统维护 - ssh开关','','{\"enable\":\"0\"}');
/*!40000 ALTER TABLE `config` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-03-29 17:47:21
