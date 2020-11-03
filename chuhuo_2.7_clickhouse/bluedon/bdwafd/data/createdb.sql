SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `waf` DEFAULT CHARACTER SET utf8 ;
USE `waf` ;

-- -----------------------------------------------------
-- Table `waf`.`t_sysinfo`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_sysinfo` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_sysinfo` (
  `time` INT NOT NULL COMMENT 'cpu used ratio',
  `cpu_ratio` TINYINT NULL,
  `total_mem` INT NULL COMMENT 'total memory',
  `used_mem` INT NULL COMMENT 'used memory',
  `total_disk` INT NULL COMMENT 'total disk space',
  `used_disk` INT NULL COMMENT 'used disk space',
  PRIMARY KEY (`time`))
ENGINE = MyISAM
COMMENT = 'system info';


-- -----------------------------------------------------
-- Table `waf`.`t_nicsflow`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_nicsflow` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_nicsflow` (
  `nic` VARCHAR(10) NOT NULL COMMENT 'NIC name',
  `mac` VARCHAR(45) NULL COMMENT 'mac address',
  `mode` VARCHAR(4) NULL COMMENT 'work mode',
  `status` TINYINT NULL COMMENT 'link status',
  `rcv_pks` INT NULL COMMENT 'received packets',
  `snd_pks` INT NULL COMMENT 'sended packets',
  `rcv_bytes` BIGINT NULL COMMENT 'received bytes',
  `snd_bytes` BIGINT NULL COMMENT 'sended bytes',
  `rcv_errs` INT NULL COMMENT 'received error packets',
  `snd_errs` INT NULL COMMENT 'sended error packets',
  `rcv_losts` INT NULL COMMENT 'lost packets when receive',
  `snd_losts` INT NULL COMMENT 'lost packets when sended',
  `rcv_ratio` INT NULL COMMENT 'receive rate',
  `snd_ratio` INT NULL COMMENT 'send rate',
  `time` INT NOT NULL,
  PRIMARY KEY (`time`, `nic`))
ENGINE = MyISAM
AUTO_INCREMENT = 1
COMMENT = 'NICS flow';


-- -----------------------------------------------------
-- Table `waf`.`t_devinfo`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_devinfo` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_devinfo` (
  `model` VARCHAR(20) NOT NULL COMMENT 'product model',
  `sys_ver` VARCHAR(20) NOT NULL COMMENT 'system version',
  `rule_ver` VARCHAR(20) NOT NULL COMMENT 'rules version',
  `serial_num` VARCHAR(30) NOT NULL COMMENT 'product serial number')
ENGINE = MyISAM
COMMENT = 'the production info';


-- -----------------------------------------------------
-- Table `waf`.`t_rulecat`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_rulecat` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_rulecat` (
  `id` INT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `desc` VARCHAR(255) NULL,
  PRIMARY KEY (`name`))
COMMENT = 'Rule Category';


-- -----------------------------------------------------
-- Table `waf`.`t_rules`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_rules` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_rules` (
  `id` INT NULL COMMENT 'our rule id',
  `realid` INT NOT NULL COMMENT 'crs real rule id',
  `name` VARCHAR(255) NULL COMMENT 'rule name',
  `content` VARCHAR(1024) NULL COMMENT 'rule content',
  `desc` VARCHAR(1024) NULL COMMENT 'description',
  `type` VARCHAR(45) NULL,
  `action` VARCHAR(45) NULL,
  `status` TINYINT NULL COMMENT '0disable 1enable',
  `update_time` INT NULL,
  `redirect_id` TINYINT NULL,
  PRIMARY KEY (`realid`))
ENGINE = MyISAM
COMMENT = 'the internal roles';


-- -----------------------------------------------------
-- Table `waf`.`t_actioncat`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_actioncat` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_actioncat` (
  `action_id` TINYINT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `desc` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`name`))
ENGINE = MyISAM
COMMENT = 'Blocking action category';


-- -----------------------------------------------------
-- Table `waf`.`t_redirectpage`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_redirectpage` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_redirectpage` (
  `redirect_id` TINYINT NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `desc` VARCHAR(255) NULL,
  `http_code` VARCHAR(255) NULL COMMENT 'http result code , e: 200 OK',
  `server` VARCHAR(255) NULL,
  `page` VARCHAR(1024) NOT NULL COMMENT 'page content, html',
  PRIMARY KEY (`redirect_id`))
COMMENT = 'redirect page set';


-- -----------------------------------------------------
-- Table `waf`.`t_httptypeset`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_httptypeset` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_httptypeset` (
  `id` TINYINT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `desc` VARCHAR(45) NULL,
  `selected` TINYINT NOT NULL DEFAULT 0 COMMENT '0:no selected 1:selected',
  PRIMARY KEY (`id`))
ENGINE = MyISAM
COMMENT = 'http request type category';


-- -----------------------------------------------------
-- Table `waf`.`t_overflowset`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_overflowset` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_overflowset` (
  `id` INT NULL COMMENT 'rule id',
  `name` VARCHAR(45) NOT NULL,
  `value` INT NOT NULL,
  `status` TINYINT NULL COMMENT '0:disable 1:enable',
  `secname` VARCHAR(100) NULL,
  PRIMARY KEY (`name`))
ENGINE = MyISAM
COMMENT = 'protect http  head overflow set';


-- -----------------------------------------------------
-- Table `waf`.`t_spiders`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_spiders` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_spiders` (
  `id` SMALLINT NOT NULL,
  `type` VARCHAR(255) NOT NULL COMMENT 'spider category',
  `name` VARCHAR(255) NOT NULL COMMENT 'spider\'s name',
  `feature` VARCHAR(45) NOT NULL COMMENT 'spider\'s http head feature',
  `ips` VARCHAR(255) NULL COMMENT 'the spider\'s ip, Multiple ip separated by \'|\',  example:1.1.1.1|2.2.2.2',
  `status` TINYINT NULL DEFAULT 1 COMMENT '0disable 1enable',
  `update_time` INT NULL,
  PRIMARY KEY (`id`))
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `waf`.`t_keywordset`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_keywordset` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_keywordset` (
  `ischecked` TINYINT NOT NULL DEFAULT 1 COMMENT '0disable, 1enable',
  `keywords` VARCHAR(2048) NULL COMMENT 'keywords, Multiple keyword separated by  \'|\'')
ENGINE = MyISAM
COMMENT = 'keywords filter set';


-- -----------------------------------------------------
-- Table `waf`.`t_baseaccessctrl`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_baseaccessctrl` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_baseaccessctrl` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `status` TINYINT NULL DEFAULT 1 COMMENT '0disable 1enable',
  `desc` VARCHAR(255) NULL COMMENT 'description',
  `src_ips` VARCHAR(100) NULL COMMENT 'ip or ips ,null mean no limits',
  `dest_ips` VARCHAR(100) NULL COMMENT 'ip or ips, null mean no limits',
  `url` VARCHAR(1024) NULL COMMENT 'the website url',
  `action` VARCHAR(45) NOT NULL,
  `realid` int(11) NOT NULL COMMENT,
  `type` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = MyISAM
COMMENT = 'base access control set';

CREATE INDEX `fk_t_baseaccessctrl_t_actioncat1_idx` ON `waf`.`t_baseaccessctrl` (`action` ASC);


-- -----------------------------------------------------
-- Table `waf`.`t_advaccessctrl`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_advaccessctrl` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_advaccessctrl` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `status` TINYINT NULL DEFAULT 1 COMMENT '0disabled 1enabled',
  `desc` VARCHAR(255) NULL,
  `src_ips` VARCHAR(100) NULL COMMENT 'ip or ips ,null mean no limit',
  `dest_ips` VARCHAR(100) NULL COMMENT 'ip or ips, null mean no limit',
  `url` VARCHAR(1024) NULL,
  `rule_id` INT NULL,
  `action` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = MyISAM
COMMENT = 'advance access control set';

CREATE INDEX `fk_t_advaccessctrl_t_actioncat1_idx` ON `waf`.`t_advaccessctrl` (`action` ASC);


-- -----------------------------------------------------
-- Table `waf`.`t_reverporxy`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_reverporxy` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_reverporxy` (
  `host` VARCHAR(255) NOT NULL COMMENT 'host name',
  `proto` VARCHAR(10) NULL COMMENT 'http/https',
  `hatype` VARCHAR(30) BINARY NULL COMMENT 'HA Algorithm:1poll, 2IP hash, 3weight',
  `cache` TINYINT NULL DEFAULT 0 COMMENT '0:no cache 1:cache',
  `helthcheck` TINYINT NULL DEFAULT 0 COMMENT '0 no check, 1 check',
  `locals` VARCHAR(1024) NULL COMMENT 'local NIC and port，format：eth0:port;eth1:port',
  `servers` VARCHAR(1024) NULL COMMENT 'servers，format：ip1:port1:weight1;ip2:port2:weight2',
  PRIMARY KEY (`host`))
ENGINE = MyISAM
COMMENT = 'the reverse proxy set';


-- -----------------------------------------------------
-- Table `waf`.`t_reportsmanage`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_reportsmanage` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_reportsmanage` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NULL,
  `type` TINYINT NULL COMMENT '1IDS report, 2 flow report, 3 access report',
  `desc` VARCHAR(255) NULL,
  `time` INT NULL COMMENT 'report create time',
  PRIMARY KEY (`id`))
ENGINE = MyISAM
COMMENT = 'the reports manage';


-- -----------------------------------------------------
-- Table `waf`.`t_cyclereport`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_cyclereport` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_cyclereport` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NULL,
  `type` TINYINT NULL COMMENT '1IDS report, 2 flow report, 3 access report',
  `desc` VARCHAR(255) NULL,
  `cycle` TINYINT NULL COMMENT '1year, 2month 3week 4day',
  `sendmail` TINYINT NULL COMMENT '0 no send mail, 1 send mail',
  `format` VARCHAR(10) NULL COMMENT 'report output format :html、doc、pdf',
  PRIMARY KEY (`id`))
ENGINE = MyISAM
COMMENT = 'the periodic report set';


-- -----------------------------------------------------
-- Table `waf`.`t_bridge`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_bridge` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_bridge` (
  `name` VARCHAR(45) NOT NULL COMMENT 'virtual bridge\'s name',
  `nics` VARCHAR(256) NULL COMMENT 'NIC name',
  `ageingtime` INT NULL,
  `stp` TINYINT NULL COMMENT '0disable 1enable',
  `forwarddelay` INT NULL,
  `maxage` INT NULL,
  `hellotime` INT NULL,
  `level` INT NULL,
  PRIMARY KEY (`name`))
ENGINE = MyISAM
COMMENT = 'the virtual net bridge set';


-- -----------------------------------------------------
-- Table `waf`.`t_nicset`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_nicset` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_nicset` (
  `nic` VARCHAR(45) NOT NULL COMMENT 'nic name',
  `ip` VARCHAR(45) NULL,
  `mask` VARCHAR(45) NULL,
  `gateway` VARCHAR(45) NULL,
  `isstart` TINYINT NULL COMMENT '0disable 1enable',
  `islink` TINYINT NULL COMMENT '0unlink 1linked',
  `workmode` VARCHAR(45) NULL,
  `desc` VARCHAR(45) NULL,
  `brgname` VARCHAR(45) NULL COMMENT 'belong which bridge',
  PRIMARY KEY (`nic`))
ENGINE = MyISAM
COMMENT = 'the NIC set';

CREATE INDEX `fk_t_nicset_t_bridges1_idx` ON `waf`.`t_nicset` (`brgname` ASC);


-- -----------------------------------------------------
-- Table `waf`.`t_staticroute`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_staticroute` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_staticroute` (
  `nic` VARCHAR(45) NULL,
  `isdefault` TINYINT NULL COMMENT '1 default  route set 0 not default',
  `dest` VARCHAR(45) NULL COMMENT 'dest ip',
  `mask` VARCHAR(45) NULL,
  `gateway` VARCHAR(45) NULL)
ENGINE = MyISAM
COMMENT = 'the static route info';


-- -----------------------------------------------------
-- Table `waf`.`t_dns`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_dns` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_dns` (
  `first` VARCHAR(45) NOT NULL,
  `second` VARCHAR(45) NULL,
  PRIMARY KEY (`first`))
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `waf`.`t_mailset`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_mailset` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_mailset` (
  `sender` VARCHAR(45) NULL COMMENT 'sender\'s mail',
  `username` VARCHAR(45) NULL,
  `password` VARCHAR(45) NULL,
  `smtpserver` VARCHAR(45) NULL,
  `smtp_port` INT NULL,
  `receiver` VARCHAR(45) NULL COMMENT 'receiver\'s mail')
ENGINE = MyISAM
COMMENT = 'the mail config';


-- -----------------------------------------------------
-- Table `waf`.`t_user`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_user` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(16) NOT NULL,
  `email` VARCHAR(255) NULL,
  `password` VARCHAR(32) NOT NULL,
  `createtime` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `role` TINYINT NOT NULL COMMENT '1system manager, 2safe manager, 3safe auditer',
  `errors` TINYINT NULL,
  `locktime` INT NULL,
  `name` VARCHAR(20) NULL,
  `phone` VARCHAR(100) NULL,
  `status` TINYINT NULL,
  PRIMARY KEY (`id`));


-- -----------------------------------------------------
-- Table `waf`.`t_sessions`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_sessions` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_sessions` (
  `username` VARCHAR(16) NOT NULL,
  `dateline` INT NOT NULL,
  `role` TINYINT NOT NULL,
  PRIMARY KEY (`username`))
ENGINE = MEMORY;


-- -----------------------------------------------------
-- Table `waf`.`t_severity`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_severity` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_severity` (
  `severity` TINYINT NOT NULL,
  `name` VARCHAR(45) NULL,
  `desc` VARCHAR(45) NULL,
  PRIMARY KEY (`severity`))
ENGINE = MyISAM
COMMENT = 'severity desc';


-- -----------------------------------------------------
-- Table `waf`.`t_userconfig`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_userconfig` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_userconfig` (
  `maxError` TINYINT(3) NOT NULL,
  `lockTime` TINYINT(5) NOT NULL,
  PRIMARY KEY (`maxError`))
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `waf`.`t_httprequesttype`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_httprequesttype` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_httprequesttype` (
  `id` TINYINT NOT NULL,
  `name` VARCHAR(255) NULL,
  `status` TINYINT NULL,
  PRIMARY KEY (`id`))
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `waf`.`t_httpver`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_httpver` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_httpver` (
  `id` TINYINT NOT NULL,
  `name` VARCHAR(45) NULL,
  `status` TINYINT NULL,
  PRIMARY KEY (`id`))
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `waf`.`t_restrictext`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_restrictext` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_restrictext` (
  `id` TINYINT NOT NULL,
  `name` VARCHAR(45) NULL,
  `status` TINYINT NULL,
  PRIMARY KEY (`id`))
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `waf`.`t_restrictheaders`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_restrictheaders` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_restrictheaders` (
  `id` TINYINT NOT NULL,
  `name` VARCHAR(45) NULL,
  `status` TINYINT NULL,
  PRIMARY KEY (`id`))
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `waf`.`t_baseconfig`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_baseconfig` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_baseconfig` (
  `wafengine` VARCHAR(20) NOT NULL COMMENT 'On|Off|DetectionOnly',
  `defaultaction` VARCHAR(10) NOT NULL,
  `ports` VARCHAR(100) NOT NULL COMMENT '80|8080',
  `deploy` VARCHAR(20) NOT NULL COMMENT 'bridge、reverse proxy',
  PRIMARY KEY (`wafengine`))
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `waf`.`t_webguard`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_webguard` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_webguard` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `url` VARCHAR(1024) NULL,
  `username` VARCHAR(45) NULL,
  `password` VARCHAR(100) NULL,
  PRIMARY KEY (`id`))
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `waf`.`t_rulefiles`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_rulefiles` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_rulefiles` (
  `id` INT NOT NULL,
  `filename` VARCHAR(255) NULL,
  `ruleids` VARCHAR(2048) NULL,
  `desc` VARCHAR(1024) NULL,
  `type` VARCHAR(45) NULL,
  PRIMARY KEY (`id`))
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `waf`.`t_ruleset`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_ruleset` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_ruleset` (
  `modelname` VARCHAR(20) NOT NULL,
  `selectedfiles` VARCHAR(1024) NULL,
  `ischecked` TINYINT NULL,
  PRIMARY KEY (`modelname`))
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `waf`.`t_userrole`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `waf`.`t_userrole` ;

CREATE TABLE IF NOT EXISTS `waf`.`t_userrole` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL,
  `roles` TEXT NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = MyISAM
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- Data for table `waf`.`t_devinfo`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_devinfo` (`model`, `sys_ver`, `rule_ver`, `serial_num`) VALUES ('BD-WAF-M4000', '1.0', '1.0', 'BD20140312001SN');

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_rulecat`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_rulecat` (`id`, `name`, `desc`) VALUES (1, 'SQLI', 'SQL注入');
INSERT INTO `waf`.`t_rulecat` (`id`, `name`, `desc`) VALUES (2, 'XSS', 'XSS跨站脚本');
INSERT INTO `waf`.`t_rulecat` (`id`, `name`, `desc`) VALUES (3, 'GENERIC', '通用攻击');
INSERT INTO `waf`.`t_rulecat` (`id`, `name`, `desc`) VALUES (4, 'PROTOCOL', 'HTTP协议保护');
INSERT INTO `waf`.`t_rulecat` (`id`, `name`, `desc`) VALUES (5, 'TROJANS', '特洛伊木马');
INSERT INTO `waf`.`t_rulecat` (`id`, `name`, `desc`) VALUES (6, 'LEAKAGE', '信息泄漏');
INSERT INTO `waf`.`t_rulecat` (`id`, `name`, `desc`) VALUES (7, 'OTHER', '其他攻击');
INSERT INTO `waf`.`t_rulecat` (`id`, `name`, `desc`) VALUES (8, 'OVERFLOW', '溢出攻击');
INSERT INTO `waf`.`t_rulecat` (`id`, `name`, `desc`) VALUES (8, 'ACCESSCTRL', '访问控制');

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_rules`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1001, 981231, '探测SQL注释符号', '(/\\*!?|\\*/|[\';]--|--[\\s\\r\\n\\v\\f]|(?:--[^-]*?-)|([^\\-&])#.*?[\\s\\r\\n\\v\\f]|;?\\\\x00)', '探测常见的SQL脚本中的注释字符，如-- /**/等', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1002, 981260, '十六进制SQL规避方法', '(?i:(?:\\A|[^\\d])0x[a-f\\d]{3,}[a-f\\d]*)+', '很多SQL注入为了逃避检测，往往将攻击内容进行十六进制编码', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1003, 981318, 'SQL常用注入测试', '(^[\\\"\'`´’‘;]+|[\\\"\'`´’‘;]+$)', '识别常见的初始SQL注入探测请求，攻击者尝试在正常的输入位置插入/追加引号字符等，看看web应用程序/数据库如何响应。', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1004, 981319, 'SQL常见操作符检测', '(?i:(\\!\\=|\\&\\&|\\|\\||>>|<<|>=|<=|<>|<=>|xor|rlike|regexp|isnull)|(?:not\\s+between\\s+0\\s+and)|(?:is\\s+null)|(like\\s+null)|(?:(?:^|\\W)in[+\\s]*\\([\\s\\d\\\"]+[^()]*\\))|(?:xor|<>|rlike(?:\\s+binary)?)|(?:regexp\\s+binary))', '通过检测SQL语句中的常见操作符来判断SQL注入攻击，如常见的：xor|rlike|regexp|isnullnot|between|and|like|in等', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1005, 950901, '永远为真条件表达式检测', '(?i:([\\s\'\\\"`´’‘\\(\\)]*?)\\b([\\d\\w]++)([\\s\'\\\"`´’‘\\(\\)]*?)(?:(?:=|<=>|r?like|sounds\\s+like|regexp)([\\s\'\\\"`´’‘\\(\\)]*?)\\2\\b|(?:!=|<=|>=|<>|<|>|\\^|is\\s+not|not\\s+like|not\\s+regexp)([\\s\'\\\"`´’‘\\(\\)]*?)(?!\\2)([\\d\\w]+)\\b))', '检测永远返回真的SQL条件语句，最常见的攻击手法如： 利用OR 1=1来返回所有记录', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1006, 981320, '数据库名字探测', '(?i:(?:m(?:s(?:ysaccessobjects|ysaces|ysobjects|ysqueries|ysrelationships|ysaccessstorage|ysaccessxml|ysmodules|ysmodules2|db)|aster\\.\\.sysdatabases|ysql\\.db)|s(?:ys(?:\\.database_name|aux)|chema(?:\\W*\\(|_name)|qlite(_temp)?_master)|d(?:atabas|b_nam)e\\W*\\(|information_schema|pg_(catalog|toast)|northwind|tempdb))', '检测输入中是否出现一些数据库系统中常见的数据库名，如：master、sysobjects等', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1007, 981301, 'select关键词检测', 'select', 'SQL关键词检测，当检测到select后威胁积分+1,默认当积分>3后阻断攻击', 'SQLI', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1008, 981302, 'show关键词检测', 'show', 'SQL关键词检测，当检测到show后积分+1,默认当积分>3后阻断攻击', 'SQLI', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1009, 981303, 'top关键词检测', 'top', 'SQL关键词检测，当检测到top后积分+1,默认当积分>3后阻断攻击', 'SQLI', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1010, 981304, 'distinct关键词检测', 'distinct', 'SQL关键词检测，当检测到distinct后积分+1,默认当积分>3后阻断攻击', 'SQLI', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1011, 981305, 'from关键词检测', 'from', 'SQL关键词检测，当检测到from后积分+1,默认当积分>3后阻断攻击', 'SQLI', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1012, 981306, 'dual关键词检测', 'dual', 'SQL关键词检测，当检测到dual后积分+1,默认当积分>3后阻断攻击', 'SQLI', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1013, 981307, 'where关键词检测', 'where', 'SQL关键词检测，当检测到where后积分+1,默认当积分>3后阻断攻击', 'SQLI', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1014, 981308, 'group by关键词检测', 'group by', 'SQL关键词检测，当检测到group by后积分+1,默认当积分>3后阻断攻击', 'SQLI', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1015, 981309, 'order by关键词检测', 'order by', 'SQL关键词检测，当检测到order by后积分+1,默认当积分>3后阻断攻击', 'SQLI', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1016, 981310, 'having关键词检测', 'having', 'SQL关键词检测，当检测到having后积分+1,默认当积分>3后阻断攻击', 'SQLI', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1017, 981311, 'limit关键词检测', 'limit', 'SQL关键词检测，当检测到limit后积分+1,默认当积分>3后阻断攻击', 'SQLI', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1018, 981312, 'offset关键词检测', 'offset', 'SQL关键词检测，当检测到offset后积分+1,默认当积分>3后阻断攻击', 'SQLI', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1019, 981313, 'union关键词检测', 'union', 'SQL关键词检测，当检测到union后积分+1,默认当积分>3后阻断攻击', 'SQLI', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1020, 981314, 'union all关键词检测', 'union all', 'SQL关键词检测，当检测到union all后积分+1,默认当积分>3后阻断攻击', 'SQLI', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1021, 981315, 'rownum as关键词检测', 'rownum as', 'SQL关键词检测，当检测到rownum as后积分+1,默认当积分>3后阻断攻击', 'SQLI', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1022, 981316, '(case关键词检测', '(case', 'SQL关键词检测，当检测到(case后积分+1,默认当积分>3后阻断攻击', 'SQLI', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1023, 950007, 'SQL盲注检测(OWASP TOP 10)', '(?i:(?:\\b(?:(?:s(?:ys\\.(?:user_(?:(?:t(?:ab(?:_column|le)|rigger)|object|view)s|c(?:onstraints|atalog))|all_tables|tab)|elect\\b.{0,40}\\b(?:substring|users?|ascii))|m(?:sys(?:(?:queri|ac)e|relationship|column|object)s|ysql\\.(db|user))|c(?:onstraint_type|harindex)|waitfor\\b\\W*?\\bdelay|attnotnull)\\b|(?:locate|instr)\\W+\\()|\\@\\@spid\\b)|\\b(?:(?:s(?:ys(?:(?:(?:process|tabl)e|filegroup|object)s|c(?:o(?:nstraint|lumn)s|at)|dba|ibm)|ubstr(?:ing)?)|user_(?:(?:(?:constrain|objec)t|tab(?:_column|le)|ind_column|user)s|password|group)|a(?:tt(?:rel|typ)id|ll_objects)|object_(?:(?:nam|typ)e|id)|pg_(?:attribute|class)|column_(?:name|id)|xtype\\W+\\bchar|mb_users|rownum)\\b|t(?:able_name\\b|extpos\\W+\\()))', 'OWASP排名前10的SQL盲注检测', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1024, 950001, 'SQL注入检测之一(OWASP TOP 10)', '(?i:(?:(?:s(?:t(?:d(?:dev(_pop|_samp)?)?|r(?:_to_date|cmp))|u(?:b(?:str(?:ing(_index)?)?|(?:dat|tim)e)|m)|e(?:c(?:_to_time|ond)|ssion_user)|ys(?:tem_user|date)|ha(1|2)?|oundex|chema|ig?n|pace|qrt)|i(?:s(null|_(free_lock|ipv4_compat|ipv4_mapped|ipv4|ipv6|not_null|not|null|used_lock))?|n(?:et6?_(aton|ntoa)|s(?:ert|tr)|terval)?|f(null)?)|u(?:n(?:compress(?:ed_length)?|ix_timestamp|hex)|tc_(date|time|timestamp)|p(?:datexml|per)|uid(_short)?|case|ser)|l(?:o(?:ca(?:l(timestamp)?|te)|g(2|10)?|ad_file|wer)|ast(_day|_insert_id)?|e(?:(?:as|f)t|ngth)|case|trim|pad|n)|t(?:ime(stamp|stampadd|stampdiff|diff|_format|_to_sec)?|o_(base64|days|seconds|n?char)|r(?:uncate|im)|an)|m(?:a(?:ke(?:_set|date)|ster_pos_wait|x)|i(?:(?:crosecon)?d|n(?:ute)?)|o(?:nth(name)?|d)|d5)|r(?:e(?:p(?:lace|eat)|lease_lock|verse)|o(?:w_count|und)|a(?:dians|nd)|ight|trim|pad)|f(?:i(?:eld(_in_set)?|nd_in_set)|rom_(base64|days|unixtime)|o(?:und_rows|rmat)|loor)|a(?:es_(?:de|en)crypt|s(?:cii(str)?|in)|dd(?:dat|tim)e|(?:co|b)s|tan2?|vg)|p(?:o(?:sition|w', 'OWASP排名前10的SQL注入检测', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1025, 959070, 'SQL注入检测之二(OWASP TOP 10)', '\\b(?i:having)\\b\\s+(\\d{1,10}|\'[^=]{1,10}\')\\s*?[=<>]|(?i:\\bexecute(\\s{1,5}[\\w\\.$]{1,5}\\s{0,3})?\\()|\\bhaving\\b ?(?:\\d{1,10}|[\\\'\\\"][^=]{1,10}[\\\'\\\"]) ?[=<>]+|(?i:\\bcreate\\s+?table.{0,20}?\\()|(?i:\\blike\\W*?char\\W*?\\()|(?i:(?:(select(.*?)case|from(.*?)limit|order\\sby)))|exists\\s(\\sselect|select\\Sif(null)?\\s\\(|select\\Stop|select\\Sconcat|system\\s\\(|\\b(?i:having)\\b\\s+(\\d{1,10})|\'[^=]{1,10}\')', 'OWASP排名前10的SQL注入检测', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1026, 959071, 'SQL注入检测之三(OWASP TOP 10)', '(?i:\\bor\\b ?(?:\\d{1,10}|[\\\'\\\"][^=]{1,10}[\\\'\\\"]) ?[=<>]+|(?i:\'\\s+x?or\\s+.{1,20}[+\\-!<>=])|\\b(?i:x?or)\\b\\s+(\\d{1,10}|\'[^=]{1,10}\')|\\b(?i:x?or)\\b\\s+(\\d{1,10}|\'[^=]{1,10}\')\\s*?[=<>])', 'OWASP排名前10的SQL注入检测', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1027, 959072, 'SQL注入检测之四(OWASP TOP 10)', '(?i)\\b(?i:and)\\b\\s+(\\d{1,10}|\'[^=]{1,10}\')\\s*?[=]|\\b(?i:and)\\b\\s+(\\d{1,10}|\'[^=]{1,10}\')\\s*?[<>]|\\band\\b ?(?:\\d{1,10}|[\\\'\\\"][^=]{1,10}[\\\'\\\"]) ?[=<>]+|\\b(?i:and)\\b\\s+(\\d{1,10}|\'[^=]{1,10}\')', 'OWASP排名前10的SQL注入检测', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1028, 959073, 'SQL注入检测之五(OWASP TOP 10)', '(?i:(?:(?:s(?:t(?:d(?:dev(_pop|_samp)?)?|r(?:_to_date|cmp))|u(?:b(?:str(?:ing(_index)?)?|(?:dat|tim)e)|m)|e(?:c(?:_to_time|ond)|ssion_user)|ys(?:tem_user|date)|ha(1|2)?|oundex|chema|ig?n|pace|qrt)|i(?:s(null|_(free_lock|ipv4_compat|ipv4_mapped|ipv4|ipv6|not_null|not|null|used_lock))?|n(?:et6?_(aton|ntoa)|s(?:ert|tr)|terval)?|f(null)?)|u(?:n(?:compress(?:ed_length)?|ix_timestamp|hex)|tc_(date|time|timestamp)|p(?:datexml|per)|uid(_short)?|case|ser)|l(?:o(?:ca(?:l(timestamp)?|te)|g(2|10)?|ad_file|wer)|ast(_day|_insert_id)?|e(?:(?:as|f)t|ngth)|case|trim|pad|n)|t(?:ime(stamp|stampadd|stampdiff|diff|_format|_to_sec)?|o_(base64|days|seconds|n?char)|r(?:uncate|im)|an)|m(?:a(?:ke(?:_set|date)|ster_pos_wait|x)|i(?:(?:crosecon)?d|n(?:ute)?)|o(?:nth(name)?|d)|d5)|r(?:e(?:p(?:lace|eat)|lease_lock|verse)|o(?:w_count|und)|a(?:dians|nd)|ight|trim|pad)|f(?:i(?:eld(_in_set)?|nd_in_set)|rom_(base64|days|unixtime)|o(?:und_rows|rmat)|loor)|a(?:es_(?:de|en)crypt|s(?:cii(str)?|in)|dd(?:dat|tim)e|(?:co|b)s|tan2?|vg)|p(?:o(?:sition|w', 'OWASP排名前10的SQL注入检测', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1029, 950908, 'SQL注入检测之六', '(?i:\\b(?:coalesce\\b|root\\@))', 'SQL注入检测', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1030, 981172, 'SQL注入字符的异常使用检测', '([\\~\\!\\@\\#\\$\\%\\^\\&\\*\\(\\)\\-\\+\\=\\{\\}\\[\\]\\|\\:\\;\\\"\\\'\\´\\’\\‘\\`\\<\\>].*?){8,}([\\~\\!\\@\\#\\$\\%\\^\\&\\*\\(\\)\\-\\+\\=\\{\\}\\[\\]\\|\\:\\;\\\"\\\'\\´\\’\\‘\\`\\<\\>].*?){8,}', '通过探测在COOKIE中出现:#*%$!等字符的次数来判断是否存在注入风险', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1031, 981173, 'SQL注入字符的异常使用检测', '([\\~\\!\\@\\#\\$\\%\\^\\&\\*\\(\\)\\-\\+\\=\\{\\}\\[\\]\\|\\:\\;\\\"\\\'\\´\\’\\‘\\`\\<\\>].*?){4,}', '通过探测URL参数中传递的值是否出现：#*%!等字符超出预期次数，来判断注入风险', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1032, 981272, '探测盲注测试', '(?i:(sleep\\((\\s*?)(\\d*?)(\\s*?)\\)|benchmark\\((.*?)\\,(.*?)\\)))', '探测通过利用sleep() or benchmark()等函数进行的盲注测试', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1033, 981244, 'SQL基础认证BYPASS之一', '(?i:(?i:\\d[\\\"\'`´’‘]\\s+[\\\"\'`´’‘]\\s+\\d)|(?:^admin\\s*?[\\\"\'`´’‘]|(\\/\\*)+[\\\"\'`´’‘]+\\s?(?:--|#|\\/\\*|{)?)|(?:[\\\"\'`´’‘]\\s*?\\b(x?or|div|like|between|and)\\b\\s*?[+<>=(),-]\\s*?[\\d\\\"\'`´’‘])|(?:[\\\"\'`´’‘]\\s*?[^\\w\\s]?=\\s*?[\\\"\'`´’‘])|(?:[\\\"\'`´’‘]\\W*?[+=]+\\W*?[\\\"\'`´’‘])|(?:[\\\"\'`´’‘]\\s*?[!=|][\\d\\s!=+-]+.*?[\\\"\'`´’‘(].*?$)|(?:[\\\"\'`´’‘]\\s*?[!=|][\\d\\s!=]+.*?\\d+$)|(?:[\\\"\'`´’‘]\\s*?like\\W+[\\w\\\"\'`´’‘(])|(?:\\sis\\s*?0\\W)|(?:where\\s[\\s\\w\\.,-]+\\s=)|(?:[\\\"\'`´’‘][<>~]+[\\\"\'`´’‘]))', '探测企图绕过SQL基础认证的尝试', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1034, 981255, 'MSSQL代码执行及信息收集检测', '(?i:(?:\\sexec\\s+xp_cmdshell)|(?:[\\\"\'`´’‘]\\s*?!\\s*?[\\\"\'`´’‘\\w])|(?:from\\W+information_schema\\W)|(?:(?:(?:current_)?user|database|schema|connection_id)\\s*?\\([^\\)]*?)|(?:[\\\"\'`´’‘];?\\s*?(?:select|union|having)\\s*?[^\\s])|(?:\\wiif\\s*?\\()|(?:exec\\s+master\\.)|(?:union select @)|(?:union[\\w(\\s]*?select)|(?:select.*?\\w?user\\()|(?:into[\\s+]+(?:dump|out)file\\s*?[\\\"\'`´’‘]))', '探测攻击者企图执行MSSQL数据库代码，及收集数据库信息的企图', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1035, 981257, 'MySQL数据库检测', '(?i:(?:,.*?[)\\da-f\\\"\'`´’‘][\\\"\'`´’‘](?:[\\\"\'`´’‘].*?[\\\"\'`´’‘]|\\Z|[^\\\"\'`´’‘]+))|(?:\\Wselect.+\\W*?from)|((?:select|create|rename|truncate|load|alter|delete|update|insert|desc)\\s*?\\(\\s*?space\\s*?\\())', '探测mysql数据库的注释区间混淆和反单引号中断的检测', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1036, 981248, '链式SQL注入检测之一', '(?i:(?:@.+=\\s*?\\(\\s*?select)|(?:\\d+\\s*?(x?or|div|like|between|and)\\s*?\\d+\\s*?[\\-+])|(?:\\/\\w+;?\\s+(?:having|and|x?or|div|like|between|and|select)\\W)|(?:\\d\\s+group\\s+by.+\\()|(?:(?:;|#|--)\\s*?(?:drop|alter))|(?:(?:;|#|--)\\s*?(?:update|insert)\\s*?\\w{2,})|(?:[^\\w]SET\\s*?@\\w+)|(?:(?:n?and|x?x?or|div|like|between|and|not |\\|\\||\\&\\&)[\\s(]+\\w+[\\s)]*?[!=+]+[\\s\\d]*?[\\\"\'`´’‘=()]))', '探测通过--#等注释符号或;等符号拼装成的链式SQL注入检测', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1037, 981277, '整数溢出攻击检测', '(?i:(?:^(-0000023456|4294967295|4294967296|2147483648|2147483647|0000012345|-2147483648|-2147483649|0000023456|2.2.80738585072007e-308|1e309)$))', '探测整数溢出攻击，比如skipfish中的魔数：2.2.80738585072007e-308', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1038, 981250, 'benchmark和sleep函数注入检测', '(?i:(?:(select|;)\\s+(?:benchmark|if|sleep)\\s*?\\(\\s*?\\(?\\s*?\\w+))', '探测在sql语句包括条件查询中的benchmark和sleep函数注入尝试', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1039, 981241, 'sql语句条件注入检测', '(?i:(?:[\\s()]case\\s*?\\()|(?:\\)\\s*?like\\s*?\\()|(?:having\\s*?[^\\s]+\\s*?[^\\w\\s])|(?:if\\s?\\([\\d\\w]\\s*?[=<>~]))', '检测sql语句查询条件语句拼装注入，如like,having等', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1040, 981252, 'MySQL字符集转换和MSSQL DOS攻击检测', '(?i:(?:alter\\s*?\\w+.*?character\\s+set\\s+\\w+)|([\\\"\'`´’‘];\\s*?waitfor\\s+time\\s+[\\\"\'`´’‘])|(?:[\\\"\'`´’‘];.*?:\\s*?goto))', '检测通过alter character set修改MySQL字符集，通过waitfor time等操作进行MSSQL DOS攻击的尝试', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1041, 981256, 'MATCH AGAINST, MERGE, EXECUTE IMMEDIATE和HAVING等注入', '(?i:(?:merge.*?using\\s*?\\()|(execute\\s*?immediate\\s*?[\\\"\'`´’‘])|(?:\\W+\\d*?\\s*?having\\s*?[^\\s\\-])|(?:match\\s*?[\\w(),+-]+\\s*?against\\s*?\\())', '检测用户提交的内容中的MATCH AGAINST, MERGE, EXECUTE IMMEDIATE，HAVING等关键词的注入', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1042, 981245, 'SQL基础认证BYPASS之二', '(?i:(?:union\\s*?(?:all|distinct|[(!@]*?)?\\s*?[([]*?\\s*?select\\s+)|(?:\\w+\\s+like\\s+[\\\"\'`´’‘])|(?:like\\s*?[\\\"\'`´’‘]\\%)|(?:[\\\"\'`´’‘]\\s*?like\\W*?[\\\"\'`´’‘\\d])|(?:[\\\"\'`´’‘]\\s*?(?:n?and|x?x?or|div|like|between|and|not |\\|\\||\\&\\&)\\s+[\\s\\w]+=\\s*?\\w+\\s*?having\\s+)|(?:[\\\"\'`´’‘]\\s*?\\*\\s*?\\w+\\W+[\\\"\'`´’‘])|(?:[\\\"\'`´’‘]\\s*?[^?\\w\\s=.,;)(]+\\s*?[(@\\\"\'`´’‘]*?\\s*?\\w+\\W+\\w)|(?:select\\s+?[\\[\\]()\\s\\w\\.,\\\"\'`´’‘-]+from\\s+)|(?:find_in_set\\s*?\\())', '探测企图绕过SQL基础认证的尝试', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1043, 981276, '基本SQL注入，在攻击MySQL,ORACLE或其他数据库时通常会出现的字符串', '(?i:(?:(union(.*?)select(.*?)from)))', '基本SQL注入，在攻击MySQL,ORACLE或其他数据库时通常会出现的字符串，通常是 union select from这样的形式', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1044, 981254, '针对Postgres的pg_sleep注入, 以及waitfor delay攻击，还有试图关闭数据库（shutdown）', '(?i:(?:select\\s*?pg_sleep)|(?:waitfor\\s*?delay\\s?[\\\"\'`´’‘]+\\s?\\d)|(?:;\\s*?shutdown\\s*?(?:;|--|#|\\/\\*|{)))', '探测针对Postgres的pg_sleep注入, 以及waitfor delay攻击，还有试图通过shutdown指令关闭数据库的操作', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1045, 981270, '针对MongoDB的基本SQL注入', '(?i:(?:\\[\\$(?:ne|eq|lte?|gte?|n?in|mod|all|size|exists|type|slice|x?or|div|like|between|and)\\]))', '探测针对MongoDB的基本sql 注入，主要关键词有：[$eq][$all][$like][$between][$and]等', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1046, 981240, '使用SQL注释符号，char函数，或其他条件语句等的注入', '(?i:(?:\\)\\s*?when\\s*?\\d+\\s*?then)|(?:[\\\"\'`´’‘]\\s*?(?:#|--|{))|(?:\\/\\*!\\s?\\d+)|(?:ch(?:a)?r\\s*?\\(\\s*?\\d)|(?:(?:(n?and|x?x?or|div|like|between|and|not)\\s+|\\|\\||\\&\\&)\\s*?\\w+\\())', '探测利用SQL注释符号-- /* #等，或者利用char(数字)函数等伪装的注入，并且检测其他between and ,like，|| &&等组成的条件语句', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1047, 981249, '链式SQL注入检测之二', '(?i:(?:[\\\"\'`´’‘]\\s+and\\s*?=\\W)|(?:\\(\\s*?select\\s*?\\w+\\s*?\\()|(?:\\*\\/from)|(?:\\+\\s*?\\d+\\s*?\\+\\s*?@)|(?:\\w[\\\"\'`´’‘]\\s*?(?:[-+=|@]+\\s*?)+[\\d(])|(?:coalesce\\s*?\\(|@@\\w+\\s*?[^\\w\\s])|(?:\\W!+[\\\"\'`´’‘]\\w)|(?:[\\\"\'`´’‘];\\s*?(?:if|while|begin))|(?:[\\\"\'`´’‘][\\s\\d]+=\\s*?\\d)|(?:order\\s+by\\s+if\\w*?\\s*?\\()|(?:[\\s(]+case\\d*?\\W.+[tw]hen[\\s(]))', '探测复杂的SQL查询语句，这些语句往往通过; () 或其他 if then when case等组成复杂的SQL语句查询', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1048, 981253, '针对MySQL和PostgreSQL的存储过程及函数注入', '(?i:(?:procedure\\s+analyse\\s*?\\()|(?:;\\s*?(declare|open)\\s+[\\w-]+)|(?:create\\s+(procedure|function)\\s*?\\w+\\s*?\\(\\s*?\\)\\s*?-)|(?:declare[^\\w]+[@#]\\s*?\\w+)|(exec\\s*?\\(\\s*?@))', '通过探测 create procedure function declare @ # exec等来确定针对MySQL和PostgreSQL的存储过程和函数注入攻击', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1049, 981242, '经典sql注入探测之一', '(?i:(?:[\\\"\'`´’‘]\\s*?(x?or|div|like|between|and)\\s*?[\\\"\'`´’‘]?\\d)|(?:\\\\\\\\x(?:23|27|3d))|(?:^.?[\\\"\'`´’‘]$)|(?:(?:^[\\\"\'`´’‘\\\\\\\\]*?(?:[\\d\\\"\'`´’‘]+|[^\\\"\'`´’‘]+[\\\"\'`´’‘]))+\\s*?(?:n?and|x?x?or|div|like|between|and|not|\\|\\||\\&\\&)\\s*?[\\w\\\"\'`´’‘][+&!@(),.-])|(?:[^\\w\\s]\\w+\\s*?[|-]\\s*?[\\\"\'`´’‘]\\s*?\\w)|(?:@\\w+\\s+(and|x?or|div|like|between|and)\\s*?[\\\"\'`´’‘\\d]+)|(?:@[\\w-]+\\s(and|x?or|div|like|between|and)\\s*?[^\\w\\s])|(?:[^\\w\\s:]\\s*?\\d\\W+[^\\w\\s]\\s*?[\\\"\'`´’‘].)|(?:\\Winformation_schema|table_name\\W))', '攻击者在找到注入点后往往会尝试从information_schema.table_name来获取数据库的元数据信息', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1050, 981246, 'SQL基础认证BYPASS之三', '(?i:(?:in\\s*?\\(+\\s*?select)|(?:(?:n?and|x?x?or|div|like|between|and|not |\\|\\||\\&\\&)\\s+[\\s\\w+]+(?:regexp\\s*?\\(|sounds\\s+like\\s*?[\\\"\'`´’‘]|[=\\d]+x))|([\\\"\'`´’‘]\\s*?\\d\\s*?(?:--|#))|(?:[\\\"\'`´’‘][\\%&<>^=]+\\d\\s*?(=|x?or|div|like|between|and))|(?:[\\\"\'`´’‘]\\W+[\\w+-]+\\s*?=\\s*?\\d\\W+[\\\"\'`´’‘])|(?:[\\\"\'`´’‘]\\s*?is\\s*?\\d.+[\\\"\'`´’‘]?\\w)|(?:[\\\"\'`´’‘]\\|?[\\w-]{3,}[^\\w\\s.,]+[\\\"\'`´’‘])|(?:[\\\"\'`´’‘]\\s*?is\\s*?[\\d.]+\\s*?\\W.*?[\\\"\'`´’‘]))', '探测企图绕过SQL基础认证的尝试', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1051, 981251, 'MySQL UDF注入，及其他的改变数据/结构的操作', '(?i:(?:create\\s+function\\s+\\w+\\s+returns)|(?:;\\s*?(?:select|create|rename|truncate|load|alter|delete|update|insert|desc)\\s*?[\\[(]?\\w{2,}))', '探测创建函数create function returns等操作，或其他的create rename truncate alter update delete insert desc等企图改变数据结构或改变数据内容的操作', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1052, 981247, '串联的基本SQL注入，和SQLLFI尝试', '(?i:(?:[\\d\\W]\\s+as\\s*?[\\\"\'`´’‘\\w]+\\s*?from)|(?:^[\\W\\d]+\\s*?(?:union|select|create|rename|truncate|load|alter|delete|update|insert|desc))|(?:(?:select|create|rename|truncate|load|alter|delete|update|insert|desc)\\s+(?:(?:group_)concat|char|load_file)\\s?\\(?)|(?:end\\s*?\\);)|([\\\"\'`´’‘]\\s+regexp\\W)|(?:[\\s(]load_file\\s*?\\())', '探测一些基本的select、create、rename、alter、update、delete等基本sql语句的串连操作，以及通过load_file等进行的LFI尝试', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (1053, 981243, '经典sql注入探测之二', '(?i:(?:[\\\"\'`´’‘]\\s*?\\*.+(?:x?or|div|like|between|and|id)\\W*?[\\\"\'`´’‘]\\d)|(?:\\^[\\\"\'`´’‘])|(?:^[\\w\\s\\\"\'`´’‘-]+(?<=and\\s)(?<=or|xor|div|like|between|and\\s)(?<=xor\\s)(?<=nand\\s)(?<=not\\s)(?<=\\|\\|)(?<=\\&\\&)\\w+\\()|(?:[\\\"\'`´’‘][\\s\\d]*?[^\\w\\s]+\\W*?\\d\\W*?.*?[\\\"\'`´’‘\\d])|(?:[\\\"\'`´’‘]\\s*?[^\\w\\s?]+\\s*?[^\\w\\s]+\\s*?[\\\"\'`´’‘])|(?:[\\\"\'`´’‘]\\s*?[^\\w\\s]+\\s*?[\\W\\d].*?(?:#|--))|(?:[\\\"\'`´’‘].*?\\*\\s*?\\d)|(?:[\\\"\'`´’‘]\\s*?(x?or|div|like|between|and)\\s[^\\d]+[\\w-]+.*?\\d)|(?:[()\\*<>%+-][\\w-]+[^\\w\\s]+[\\\"\'`´’‘][^,]))', '探测一些攻击者在攻击开始阶段尝试对数据库执行多种不同的查询操作，每次传送不同的查询条件，根据反馈结果来猜测数据库注入点和数据库结构的操作', 'SQLI', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3021, 958976, '在PHP中注入其他PHP代码(OWASP TOP 10)', '(?i)(?:\\b(?:f(?:tp_(?:nb_)?f?(?:ge|pu)t|get(?:s?s|c)|scanf|write|open|read)|gz(?:(?:encod|writ)e|compress|open|read)|s(?:ession_start|candir)|read(?:(?:gz)?file|dir)|move_uploaded_file|(?:proc_|bz)open|call_user_func)|\\$_(?:(?:pos|ge)t|session))\\b', '该规则检测尝试在http请求中输入php代码尝试注入到php中：$_post $_get $_session gzopen gzcompress session_start scandir', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3020, 959151, '在PHP中注入XML的攻击(OWASP TOP 10)', '<\\?(?!xml)', '该规则检测尝试在php代码中注入xml代码的尝试：<?xml', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3019, 950006, '系统命令注入(OWASP TOP 10)', '(?:\\b(?:(?:n(?:et(?:\\b\\W+?\\blocalgroup|\\.exe)|(?:map|c)\\.exe)|t(?:racer(?:oute|t)|elnet\\.exe|clsh8?|ftp)|(?:w(?:guest|sh)|rcmd|ftp)\\.exe|echo\\b\\W*?\\by+)\\b|c(?:md(?:(?:\\.exe|32)\\b|\\b\\W*?\\/c)|d(?:\\b\\W*?[\\\\/]|\\W*?\\.\\.)|hmod.{0,40}?\\+.{0,3}x))|[\\;\\|\\`]\\W*?\\b(?:(?:c(?:h(?:grp|mod|own|sh)|md|pp)|p(?:asswd|ython|erl|ing|s)|n(?:asm|map|c)|f(?:inger|tp)|(?:kil|mai)l|(?:xte)?rm|ls(?:of)?|telnet|uname|echo|id)\\b|g(?:\\+\\+|cc\\b)))', '该规则检测可能的系统命令注入：net.ext nmap.exe nc.exe traceroute tracert telnet.exe tclsh tftp ftp.exe echo cmd cd chmod等', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3018, 950002, '系统命令访问(OWASP TOP 10)', '\\b(?:(?:n(?:map|et|c)|w(?:guest|sh)|telnet|rcmd|ftp)\\.exe\\b|cmd(?:(?:32)?\\.exe\\b|\\b\\W*?\\/c))', '该规则检测以下可能的系统命令访问：nmap net nc telnet ftp cmd32.exe', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3017, 950005, '远程文件访问(OWASP TOP 10)', '(?:\\b(?:\\.(?:ht(?:access|passwd|group)|www_?acl)|global\\.asa|httpd\\.conf|boot\\.ini)\\b|\\/etc\\/)', '该规则检测COOKIE或url参数中的可能文件注入，主要通过以下关键词检测实现：httpd.conf boot.ini /etc/ .htaccess .htpasswd .htgroup', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3016, 950000, 'SESSION加固(OWASP TOP 10)', 'jsessionid aspsessionid asp.net_sessionid phpsession phpsessid weblogicsession session_id session-id cfid cftoken cfsid jservsession jwsession', '检测可能的SESSION加固攻击，当来源为空时通过在http请求中检测jsessionid aspsessionid asp.net_sessionid phpsession phpsessid weblogicsession session_id session-id cfid cftoken cfsid jservsession jwsession等来实现', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3015, 950003, 'SESSION加固(OWASP TOP 10)', 'jsessionid aspsessionid asp.net_sessionid phpsession phpsessid weblogicsession session_id session-id cfid cftoken cfsid jservsession jwsession', '检测可能的SESSION加固攻击，当来源为外站时通过在http请求中检测jsessionid aspsessionid asp.net_sessionid phpsession phpsessid weblogicsession session_id session-id cfid cftoken cfsid jservsession jwsession等来实现', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3014, 950009, 'SESSION加固(OWASP TOP 10)', '(?i)(?:\\.cookie\\b.*?;\\W*?(?:expires|domain)\\W*?=|\\bhttp-equiv\\W+set-cookie\\b)', '检测可能的SESSION加固攻击,通过在http请求中检测cookie;expires=;domain=;set cookie;http-equiv等来实现', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3013, 950120, 'RFI的主机名和web服务器的不一致', '^(?:ht|f)tps?://(.*)$', '当http请求中存在任何url格式的内容时，并且其中的主机和web服务器的不一致时，有可能存在RFI攻击。如http请求内容中有如下格式的东西：http://other.com', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3012, 950119, '以问号（？）结束RFI数据', '^(?i)(?:ft|htt)ps?(.*?)\\?+$', '该规则检测在http请求中，以?结束的RFI攻击数据，如：http://test.com?', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3010, 950117, 'URL中有IP地址', '^(?i)(?:ht|f)tps?:\\/\\/(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3})', '该规则检测URL中是否含有ip地址，来检测可能的RFI攻击', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3011, 950118, 'PHP的Include函数', '(?i:(\\binclude\\s*\\([^)]*|mosConfig_absolute_path|_CONF\\[path\\]|_SERVER\\[DOCUMENT_ROOT\\]|GALLERY_BASEDIR|path\\[docroot\\]|appserv_root|config\\[root_dir\\])=(ht|f)tps?:\\/\\/)', '该规则检测在http的query_string或请求体中是否有php的include()函数等,来检测可能的RFI攻击', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3009, 950911, 'http响应分片(可能出现的分片内容检测)', '(?:\\bhttp\\/(?:0\\.9|1\\.[01])|<(?:html|meta)\\b)', '该规则检测在http头或cookie中的字段内容是否含有：http/0.9 http/1.0 http/1.1 或者 <html <meta等，来检测可能的http响应分片攻击', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3008, 950910, 'http响应分片(逗号的检测)', '[\\n\\r](?:content-(type|length)|set-cookie|location):', '该规则在http头中探测头中或cookie中的字段内容是否有：content-type: content-length: set-cookie: location:等，来防止用户来将自己输入的内容直接在应答中返回，达到http响应分片的目的', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3007, 950012, 'http请求走私(OWASP TOP 10)', ',', '该规则探测在http头Content-Length, Transfer-Encoding中的逗号(,),比如：Content-Length: 0, 44的意思就是有两个Content-Length,一个值是0，一个是44，apache处理这样的头就好像处理多个Cookie一样', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3005, 950018, 'UPDF XSS', 'http:\\/\\/[\\w\\.]+?\\/.*?\\.pdf\\b[^\\x0d\\x0a]*#', '该规则会寻找包含在QUERY_STRING中的＃片段内容', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3006, 950019, '邮件命令注入', '[\\n\\r]\\s*\\b(?:to|b?cc)\\b\\s*:.*?\\@', '该规则会检测用户输入数据中的邮件命令注入,如：to:111@bluedon.cn 或 cc:111@bluedon.cn 或 bcc:111@bluedon.cn等', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3003, 950010, 'LDAP注入(OWASP TOP 10)', '(?:\\((?:\\W*?(?:objectc(?:ategory|lass)|homedirectory|[gu]idnumber|cn)\\b\\W*?=|[^\\w\\x80-\\xFF]*?[\\!\\&\\|][^\\w\\x80-\\xFF]*?\\()|\\)[^\\w\\x80-\\xFF]*?\\([^\\w\\x80-\\xFF]*?[\\!\\&\\|])', '该规则通过查找常用的LDAP数据结构内容来达到防止LDAP注入,如：objectcategory = homedirectory =等', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3004, 950011, 'SSI注入(OWASP TOP 10)', '<!--\\W*?#\\W*?(?:e(?:cho|xec)|printenv|include|cmd)', '该规则检测常见的服务器站点包含格式的数据。如：<!--#echo <!--#exec <!--#printenv <!--#include <!--#cmd', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3002, 950008, 'Coldfusion注入(OWASP TOP 10)', '\\bcf(?:usion_(?:d(?:bconnections_flush|ecrypt)|set(?:tings_refresh|odbcini)|getodbc(?:dsn|ini)|verifymail|encrypt)|_(?:(?:iscoldfusiondatasourc|getdatasourceusernam)e|setdatasource(?:password|username))|newinternal(?:adminsecurit|registr)y|admin_registry_(?:delete|set)|internaldebug|execute)\\b', '该规则会检测用户输入中是否会出现一些未定义的Coldfusion管理函数名称，通过阻断这样的输入，来阻断可能的Coldfusion注入攻击', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3001, 950907, '操作系统命令注入(OWASP TOP 10)', '(?i:(?:[\\;\\|\\`]\\W*?\\bcc|\\b(wget|curl))\\b|\\/cc(?:[\\\'\\\"\\|\\;\\`\\-\\s]|$))', '该规则会查找一些企图访问操作系统命令的尝试，比如：curl、wget、cc等，这些命令经常被攻击者用来从受害者网站向外发出网络链接来下载或编译安装恶意工具程序', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3022, 958977, 'PHP注入攻击(OWASP TOP 10)', 'allow_url_include= safe_mode= suhosin.simulation= disable_functions= open_basedir= auto_prepend_file= php://input', '该规则在http请求数据中检测以下关键词：allow_url_include= safe_mode= suhosin.simulation= disable_functions= open_basedir= auto_prepend_file= php://input', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (3023, 960024, '启发式检测(非单词字符检测）', '\\W{4,}', '该规则在http请求的参数中检测连续等于或超过4次的非单词字符的出现', 'GENERIC', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4001, 960911, 'URI请求格式验证', '!^(?i:(?:[a-z]{3,10}\\s+(?:\\w{3,7}?://[\\w\\-\\./]*(?::\\d+)?)?/[^?#]*(?:\\?[^#\\s]*)?(?:#[\\S]*)?|connect (?:\\d{1,3}\\.){3}\\d{1,3}\\.?(?::\\d+)?|options \\*)\\s+[\\w\\./]+|get /[^?#]*(?:\\?[^#\\s]*)?(?:#[\\S]*)?)$', '该规则规定了RFC规范的URI格式：\"http:\" \"//\" host [ \":\" port ] [ abs_path [ \"?\" query ]] ,并同时规定了CONNECT、OPTIONS、GET请求时的正确格式', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4002, 981227, 'multipart/form-data内容逃避', '[\'\\\";=]', '该规则检测在请求中利用Content-Disposition:头来偷传multipart/form-data的情况，比如：Content-Disposition: form-data; name=\"fileRap\"; filename=\"file=.txt\"', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4003, 960912, '请求 Body是否正确', '!@eq 0', '该规则确定用户的请求体是否被正确的处理了，如果有错误将被阻断', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4004, 960914, '严格的Multipart数据解析检查', '!@eq 0', '该规则严格检查用户提交的窗体数据（multipart/form-data）,如果该规则对您的环境太严格，可以停用或修改规则动作为仅记录', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4005, 960915, '未匹配的Multipart Boundary检查', '!@eq 0', '该规则探测Multipart解析器探测到的可能的未匹配boundary', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4006, 960016, 'Content-Length的内容只能数字', '!^\\d+$', '该规则检测http请求头中Content-Length字段的内容是否是数字，按RFC的要求必须是数字', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4007, 960011, 'Get或Head请求不能有请求体', '^(?:GET|HEAD)$', '按标准规范Get或Head请求可以有请求体，但在实际环境中很少使用这个特性，因为黑客可能利用该特性发送一些请求体到一些不知情的web应用程序，来达到攻击目的', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4008, 960012, 'Post请求都要求有Content-Length字段', '^POST$', '该规则检测到如果请求是Post，则要求在请求头中必须有Content-Length字段的内容', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4009, 960902, '拒绝请求字段Content-Encoding的内容为Identity', '^Identity$', 'identity编码只能用在Accept-Encoding头中，而不能用在Content-Encoding中,如果使用了，该规则将阻断', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4010, 960022, 'Expect只是HTTP/1.1的一个属性', '@contains 100-continue', 'Expect只是HTTP/1.1的属性，所以该规则检测请求的http协议版本，如果是HTTP/1.0，但请求头中有Expect字段，该规则将阻断', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4011, 960020, 'HTTP/1.1要求Pragma和Cache-Control必须成对出现', '@eq 1', 'RFC规范要求HTTP/1.1中当有Pragma字段的时候必须也有Cache-Control字段，否则本规则将阻断', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4012, 958291, 'Range的字节范围不能从0开始', '@beginsWith bytes=0-', '该规则探测HTTP请求头中的Range字段的内容是否是以0开始的，比如Range:bytes=0-，一般浏览器都不会这么做，但很多机器人或爬虫程序可能会违背RFC这么干', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4013, 958230, 'Range、Request-Range内容后字节要大于前字节', '(\\d+)\\-(\\d+)\\,', '该规则检测Range或Request-Range的内容是否接受字节大于起始字节,如：Range:bytes=455-255,这样的内容将会被阻断', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4014, 958231, 'Range、Request-Range定义子字节范围过多', '^bytes=(\\d+)?\\-(\\d+)?\\,\\s?(\\d+)?\\-(\\d+)?\\,\\s?(\\d+)?\\-(\\d+)?\\,\\s?(\\d+)?\\-(\\d+)?\\,\\s?(\\d+)?\\-(\\d+)?\\,', '该规则检测Range或Request-Range中定义的以逗号分割的子字节范围是否过多,如：Range:bytes=500-600,601-999,一般子范围不超过5个', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4015, 958295, 'Connection中不能有冲突的内容', '\\b(keep-alive|close),\\s?(keep-alive|close)\\b', '该规则检测Connection中是的内容是否冲突，如：keep-alive,close并存将被阻断', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4016, 950107, 'URI的URL编码校验', '\\%((?!$|\\W)|[0-9a-fA-F]{2}|u[0-9a-fA-F]{4})', '该规则检测URI的内容是否有非URL编码的内容出现，如果有则认为可能有攻击', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4017, 950109, 'QUERY_STRING中的ARGS的URL编码校验', '\\%((?!$|\\W)|[0-9a-fA-F]{2}|u[0-9a-fA-F]{4})', '该规则检测请求串中的参数的内容，是否都是有效的URL编码，否则阻断', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4018, 950108, '请求Body的URL编码校验', '\\%((?!$|\\W)|[0-9a-fA-F]{2}|u[0-9a-fA-F]{4})', '该规则当请求类型是application\\/x-www-form-urlencoded时，检测请求体的内容是否都是有效的URL编码', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4019, 950801, 'UTF8编码校验', '@validateUtf8Encoding', '当用户的网站是utf8编码的时候，该规则校验用户上传的信息是否符合Utf8编码', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4020, 950116, '禁止unicode全宽字符编码', '\\%u[fF]{2}[0-9a-fA-F]{2}', '该规则检测用户URI和请求体中是否有unicode全宽字符编码，如：%uffae，有的将被认为是可能的攻击，将阻断', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4021, 960901, '限制请求的参数或内容必须为可打印字符1-255', '@validateByteRange 1-255', '该规则检测用户的请求数据,包括请求参数、内容或请求头内容等必须是1-255内的可见字符', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4022, 960018, '当开通严格限制后，将限制字符范围32-126', '@validateByteRange 32-126', '如果开通了严格限制模式，该规则检测用户的请求数据,包括请求参数、内容或请求头内容等必须是32-126内的可见字符', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4501, 960008, '请求头中缺少Host(OWASP TOP 10)', '@eq 0', '该规则检测用户上传的请求头中是否缺少Host字段，如果缺少，则阻断', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4502, 960007, '请求头中Host内容为空', '^$', '该规则检测请求头中Host的内容是否未空，为空则阻断', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4503, 960015, '请求头中缺少Accept(OWASP TOP 10)', '@eq 0', '该规则检测用户上传的请求头，看是否缺少Accetp头，当动作为非OPTIONS，而又缺少Accept头时将阻断', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4504, 960021, '请求头中的Accept的内容为空', '^$', '该规则检测当用户Http请求动作为非OPTIONS时，请求头中的Accetp的内容是否为空，为空则阻断', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4505, 960009, '请求头中缺少User-Agent头(OWASP TOP 10)', '@eq 0', '该规则检测http请求头中是否缺少User-Agent，如缺少将阻断', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4506, 960006, '请求头中的User-Agent的内容为空', '^$', '该规则检测http请求头中的User-Agent字段的内容是否为空，为空则阻断', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4507, 960904, '有请求内容的请求头中缺少Content-Type', '@eq 0', '该规则检测当请求头中的Content-Length存在，并且内容不为零的时候，是否在请求头中有Content-Type字段，如没，则web应用程序不知道怎么解析请求数据，阻断', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (4508, 960017, 'Host的内容是IP地址(OWASP TOP 10)', '^[\\d.:]+$', '该规则检测Host的内容是否是数字和.组成的IP地址，或者再带上端口号，如：1.1.1.1：80,是则阻断，因为很多网络蠕虫或自动化程序都是通过IP段扫描来传播的', 'PROTOCOL', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (5001, 950110, '通过x_key头访问后门(OWASP TOP 10)', 'x_(?:key|file)', '该规则检测Http请求头中是否有x_key***,x_file***这样的头字段，如果存在则可能是攻击者试图访问后门程序，阻断', 'TROJANS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (5002, 950921, '访问root.exe后门程序(OWASP TOP 10)', 'root\\.exe', '该规则检测uri请求中的文件名，如果访问root.exe文件，则阻断', 'TROJANS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (5003, 950922, '通过响应判断后门反问(OWASP TOP 10)', '(?:<title>[^<]*?(?:\\b(?:(?:c(?:ehennemden|gi-telnet)|gamma web shell)\\b|imhabirligi phpftp)|(?:r(?:emote explorer|57shell)|aventis klasvayv|zehir)\\b|\\.::(?:news remote php shell injection::\\.| rhtools\\b)|ph(?:p(?:(?: commander|-terminal)\\b|remoteview)|vayv)|myshell)|\\b(?:(?:(?:microsoft windows\\b.{0,10}?\\bversion\\b.{0,20}?\\(c\\) copyright 1985-.{0,10}?\\bmicrosoft corp|ntdaddy v1\\.9 - obzerve \\| fux0r inc)\\.|(?:www\\.sanalteror\\.org - indexer and read|haxplor)er|php(?:konsole| shell)|c99shell)\\b|aventgrup\\.<br>|drwxr))', '该规则检测web应用程序给用户返回的响应，如果响应中含有：remote explorer,r57shell,gamma web shell, php commander,myshell,php konsole,c99shell等,如有则可能是后门访问的响应，阻断', 'TROJANS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6001, 970007, 'Zope web服务器信息泄漏(OWASP TOP 10)', '<h2>Site Error<\\/h2>.{0,20}<p>An error was encountered while publishing this resource\\.', '该规则检测服务器响应页面是否泄漏Zope服务器的相关信息，如：Site Error   An error was encountered while publishing this resource ***', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6002, 970008, 'Cold Fusion信息泄漏(OWASP TOP 10)', '\\bThe error occurred in\\b.{0,100}: line\\b.{0,1000}\\bColdFusion\\b.*?\\bStack Trace \\(click to expand\\)', '该规则检测服务器响应页面是否会泄漏Cold Fusion的相关信息，如：The error occurred in *** : line *** ColdFusion', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6003, 970009, 'PHP信息泄漏(OWASP TOP 10)', '<b>Warning<\\/b>.{0,100}?:.{0,1000}?\\bon line\\b', '该规则检测服务器响应页面是否会泄漏PHP的相关信息，如：Warning *** :on line', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6004, 970010, 'ISA服务器信息泄漏(OWASP TOP 10)', '\\b403 Forbidden\\b.*?\\bInternet Security and Acceleration Server\\b\\', '该规则检测服务器响应页面是否会泄漏ISA服务器相关的信息，如：403 Forbidden *** Internet Security and Acceleration Server', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6005, 970012, '微软Office文档属性信息泄漏(OWASP TOP 10)', '<o:documentproperties>', '该规则检测服务器响应页面是否泄漏微软Office文档的属性信息，如：通过<o:documentproperties>泄漏', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6006, 970903, 'ASP/JSP源代码泄漏(OWASP TOP 10)', '\\<\\%', '该规则检测服务器响应页面内容是否有ASP/JSP的源代码泄漏，如：<%***', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6007, 970016, 'Cold Fusion源代码泄漏(OWASP TOP 10)', '<cf', '该规则检测服务器响应页面内容是否有Cold Fusion的源代码泄漏，如：<cf***', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6008, 970018, 'IIS缺省安装目录泄漏', '[a-z]:\\\\\\\\inetpub\\b', '该规则检测服务器响应页面内容是否泄漏了IIS安装在缺省安装目录，如：c:\\inetpub', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6009, 970901, 'Web应用程序不可用，5XX错误(OWASP TOP 10)', '^5\\d{2}$', '该规则检测服务器返回的状态码，如果是5XX错误码，则表示web应用程序不可用，该规则将阻止5XX错误。', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6010, 970118, 'Web应用程序不可用信息泄漏(OWASP TOP 10)', '(?:Microsoft OLE DB Provider for SQL Server(?:<\\/font>.{1,20}?error \'800(?:04005|40e31)\'.{1,40}?Timeout expired| \\(0x80040e31\\)<br>Timeout expired<br>)|<h1>internal server error<\\/h1>.*?<h2>part of the server has crashed or it has a configuration error\\.<\\/h2>|cannot connect to the server: timed out)', '该规则检测服务器响应页面内容是否泄漏了相关的web应用程序信息。如：Microsoft OLE DB Provider for SQL Server (0x80040e31) Timeout expired', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6011, 970021, 'WebLogic信息泄漏', '<title>JSP compile error<\\/title>', '该规则检测当服务器返回状态码为500的时候，响应页面是否泄漏WebLogic的信息，如：<title>JSP compile error</title>', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6012, 970011, '文件或目录名信息泄漏(OWASP TOP 10)', 'href\\s?=[\\s\\\"\\\']*[A-Za-z]\\:\\x5c([^\\\"\\\']+)', '该规则检测服务器响应页面内容是否泄漏文件或目录信息。如：herf = 文件路径', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6013, 970014, 'ASP/JSP源代码泄漏(OWASP TOP 10)', '(?:\\b(?:(?:s(?:erver\\.(?:(?:(?:htm|ur)lencod|execut)e|createobject|mappath)|cripting\\.filesystemobject)|(?:response\\.(?:binary)?writ|vbscript\\.encod)e|wscript\\.(?:network|shell))\\b|javax\\.servlet)|\\.(?:(?:(?:createtex|ge)t|loadfrom)file|addheader)\\b|<jsp:)\\', '该规则检测服务器响应页面内容是否有JSP/ASP源代码泄漏。如：server.htmlencode,server.execute,<jsp:***等', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6014, 970015, 'PHP源代码泄漏(OWASP TOP 10)', '(?:\\b(?:f(?:tp_(?:nb_)?f?(?:ge|pu)t|get(?:s?s|c)|scanf|write|open|read)|gz(?:(?:encod|writ)e|compress|open|read)|s(?:ession_start|candir)|read(?:(?:gz)?file|dir)|move_uploaded_file|(?:proc_|bz)open|call_user_func)|\\$_(?:(?:pos|ge)t|session))\\b', '该规则检测服务器响应页面内容是否有PHP源代码泄漏。如：fgets ***,fget ***, readdir ***,$_post, $_get, $_session', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6015, 970902, 'xml中的PHP源代码泄漏(OWASP TOP 10)', '<\\?(?!xml)', '该规则检测服务器响应页面中的xml内容中是否有PHP源代码泄漏。', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6016, 970002, '统计页面信息泄漏', '\\b(?:Th(?:is (?:summary was generated by.{0,100}?(?:w(?:ebcruncher|wwstat)|analog|Jware)|analysis was produced by.{0,100}?(?:calamaris|EasyStat|analog)|report was generated by WebLog)|ese statistics were produced by (?:getstats|PeLAB))|[gG]enerated by.{0,100}?[Ww]ebalizer)\\b', '该规则检测服务器响应页面中是否会泄漏统计页面中包含一些信息。如：This summary was generated by ***(wwwstat)', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6017, 970003, '数据库错误信息泄漏(OWASP TOP 10)', '(?:\\b(?:(?:s(?:elect list because it is not contained in (?:an aggregate function and there is no|either an aggregate function or the) GROUP BY clause|upplied argument is not a valid (?:PostgreSQL result|O(?:racle|DBC)|M(?:S |y)SQL))|S(?:yntax error converting the \\w+ value .*? to a column of data type|QL Server does not exist or access denied)|Either BOF or EOF is True, or the current record has been deleted(. Requested|; the operation)|The column prefix .{0,50}? does not match with a table name or alias name used in the query|Could not find server \'\\w+\' in sysservers\\. execute sp_addlinkedserver)\\b|microsoft jet database engine error \'8|Microsoft Access Driver|JET Database Engine|Access Database Engine|ORA-\\d{5}: |ORA-[0-9][0-9][0-9][0-9]|Oracle error|Oracle.*?Driver|Warning.*?Woci_.*?|Warning.*?Wora_.*?|Un(?:closed quotation mark before the character string\\b|able to connect to PostgreSQL server:)|PostgreSQL query failed:|PostgreSQL.*?ERROR|Warning.*?Wpg_.*?|valid PostgreSQL result|Npgsql.|(?:Microsoft OLE', '该规则检测服务器响应页面中是否会泄漏数据库的一些错误信息。如：SQL Server does not exist or access denied,PostgreSQL *** ERROR', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6018, 970004, 'IIS错误信息泄漏(OWASP TOP 10)', '(?:\\b(?:A(?:DODB\\.Command\\b.{0,100}?\\b(?:Application uses a value of the wrong type for the current operation\\b|error\')| trappable error occurred in an external object\\. The script cannot continue running\\b)|Microsoft VBScript (?:compilation (?:\\(0x8|error)|runtime (?:Error|\\(0x8))\\b|Object required: \'|error \'800)|<b>Version Information:<\\/b>(?:&nbsp;|\\s)(?:Microsoft \\.NET Framework|ASP\\.NET) Version:|>error \'ASP\\b|An Error Has Occurred|>Syntax error in string in query expression|\\/[Ee]rror[Mm]essage\\.aspx?\\?[Ee]rror\\b)', '该规则检测服务器响应页面，看在IIS错误信息页面中是否会泄漏信息。如泄漏.net版本信息：Microsoft .NET Framework Version:***', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6019, 970904, 'IIS的404错误页面泄漏信息(OWASP TOP 10)', '\\bServer Error in.{0,50}?\\bApplication\\b', '该规则检测IIS的404错误页面，看是否泄漏信息。如泄漏web应用程序相关的信息：Server Error in *** Application', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (6020, 970013, '目录列表泄漏(OWASP TOP 10)', '(?:<(?:TITLE>Index of.*?<H|title>Index of.*?<h)1>Index of|>\\[To Parent Directory\\]<\\/[Aa]><br>)', '该规则检测服务器响应页面中是否泄漏服务端的目录列表。一般目录列表页面可能包含以下信息：[To Parent Directory], 标题一般是Index of等', 'LEAKAGE', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8110, 973316, '针对IE的XSS过滤24(OWASP TOP 10)', '(?i:[ /+\\t\\\"\\\'`]style[ /+\\t]*?=.*([:=]|(&#x?0*((58)|(3A)|(61)|(3D));?)).*?([(\\\\\\\\]|(&#x?0*((40)|(28)|(92)|(5C));?)))', ' 测针对IE的特殊编码内容，如： style=...&#x0058;...&#x0040;', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8111, 973325, '针对IE的XSS过滤25(OWASP TOP 10)', '(?i:[ /+\\t\\\"\\\'`]on\\[a-z]\\[a-z]\\[a-z]+?[ +\\t]*?=.)', '检测针对IE的内容，如： /on...] =...', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8112, 973319, '检测datasrc', '(?i:[ /+\\t\\\"\\\'`]datasrc[ +\\t]*?=.)', '', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8108, 973329, '针对IE的XSS过滤22(OWASP TOP 10)', '(?i:<form.*?>)', ' 检测针对IE的内容，如： <form...>', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8109, 973328, '针对IE的XSS过滤23(OWASP TOP 10)', '(?i:<isindex[ /+\\t>])', ' 检测针对IE的内容，如： <isindex>...', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8107, 973332, '针对IE的XSS过滤21(OWASP TOP 10)', '(?i:[\\\"\\\'][ ]*(([^a-z0-9~\\_:\\\' ])|(in)).*?(((l|(\\\\\\\\u006C))(o|(\\\\\\\\u006F))(c|(\\\\\\\\u0063))(a|(\\\\\\\\u0061))(t|(\\\\\\\\u0074))(i|(\\\\\\\\u0069))(o|(\\\\\\\\u006F))(n|(\\\\\\\\u006E)))|((n|(\\\\\\\\u006E))(a|(\\\\\\\\u0061))(m|(\\\\\\\\u006D))(e|(\\\\\\\\u0065)))|((o|(\\\\\\\\u006F))(n|(\\\\\\\\u006E))(e|(\\\\\\\\u0065))(r|(\\\\\\\\u0072))(r|(\\\\\\\\u0072))(o|(\\\\\\\\u006F))(r|(\\\\\\\\u0072)))|((v|(\\\\\\\\u0076))(a|(\\\\\\\\u0061))(l|(\\\\\\\\u006C))(u|(\\\\\\\\u0075))(e|(\\\\\\\\u0065))(O|(\\\\\\\\u004F))(f|(\\\\\\\\u0066)))).*?=)', ' 检测针对IE的特殊编码内容，如： \" in ... \\\\u006C\\\\u006F...', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8106, 973344, '针对IE的XSS过滤20(OWASP TOP 10)', '(?i:[\\\"\\\'][ ]*(([^a-z0-9~\\_:\\\' ])|(in)).+?[\\[].*?[\\]].*?=)', ' 检测针对IE的内容，如： \" in ... [...]...=', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8105, 973333, '针对IE的XSS过滤19(OWASP TOP 10)', '(?i:[\\\"\\\'][ ]*(([^a-z0-9~\\_:\\\' ])|(in)).+?[.].+?=)', ' 检测针对IE的内容，如： \" in . ... =', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8104, 973334, '针对IE的XSS过滤18(OWASP TOP 10)', '(?i:[\\\"\\\'].*?\\)[ ]*(([^a-z0-9~\\_:\\\' ])|(in)).+?\\', ' 检测针对IE的内容，如： \"...) in ...(...', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8103, 973335, '针对IE的XSS过滤17(OWASP TOP 10)', '(?i:[\\\"\\\'][ ]*(([^a-z0-9~\\_:\\\' ])|(in)).+?\\(.*?\\))', ' 检测针对IE的内容，如： \" in ...(...)', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8102, 973347, '针对IE的XSS过滤16(OWASP TOP 10)', '(?i:[\\\"\\\'].*?[,].*(((v|(\\\\\\\\u0076)|(\\\\166)|(\\\\x76))[^a-z0-9]*(a|(\\\\\\\\u0061)|(\\\\141)|(\\\\x61))[^a-z0-9]*(l|(\\\\\\\\u006C)|(\\\\154)|(\\\\x6C))[^a-z0-9]*(u|(\\\\\\\\u0075)|(\\\\165)|(\\\\x75))[^a-z0-9]*(e|(\\\\\\\\u0065)|(\\\\145)|(\\\\x65))[^a-z0-9]*(O|(\\\\\\\\u004F)|(\\\\117)|(\\\\x4F))[^a-z0-9]*(f|(\\\\\\\\u0066)|(\\\\146)|(\\\\x66)))|((t|(\\\\\\\\u0074)|(\\\\164)|(\\\\x74))[^a-z0-9]*(o|(\\\\\\\\u006F)|(\\\\157)|(\\\\x6F))[^a-z0-9]*(S|(\\\\\\\\u0053)|(\\\\123)|(\\\\x53))[^a-z0-9]*(t|(\\\\\\\\u0074)|(\\\\164)|(\\\\x74))[^a-z0-9]*(r|(\\\\\\\\u0072)|(\\\\162)|(\\\\x72))[^a-z0-9]*(i|(\\\\\\\\u0069)|(\\\\151)|(\\\\x69))[^a-z0-9]*(n|(\\\\\\\\u006E)|(\\\\156)|(\\\\x6E))[^a-z0-9]*(g|(\\\\\\\\u0067)|(\\\\147)|(\\\\x67)))).*?:)', ' 检测针对IE的特殊编码内容，如： \\\\u0074 \\\\u0076等。', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8100, 973318, '针对IE的XSS过滤14(OWASP TOP 10)', '(?i:<APPLET[ /+\\t>])', ' 检测针对IE的如下内容，如： <APPLET> ...', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8101, 973317, '针对IE的XSS过滤15(OWASP TOP 10)', '(?i:<OBJECT[ /+\\t].*?((type)|(codetype)|(classid)|(code)|(data))[ /+\\t]*=)', ' 检测针对IE的如下内容，如： <OBJECT type = ...', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8098, 973321, '针对IE的XSS过滤12(OWASP TOP 10)', '(?i:<LINK[ /+\\t].*?href[ /+\\t]*=)', ' 检测针对IE的如下内容，如： <LINK href = ...', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8099, 973320, '针对IE的XSS过滤13(OWASP TOP 10)', '(?i:<BASE[ /+\\t].*?href[ /+\\t]*=)', ' 检测针对IE的如下内容，如： <BASE href = ...', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8097, 973348, '针对IE的XSS过滤11(OWASP TOP 10)', '(?i:<META[ /+\\t].*?charset[ /+\\t]*=)', ' 检测针对IE的如下内容，如： <META charset = ...', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8095, 973323, '针对IE的XSS过滤9(OWASP TOP 10)', '(?i:<[?]?import[ /+\\t].*?implementation[ /+\\t]*=)', ' 检测针对IE的如下内容，如： <import implementation= <EMBED src=....', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8096, 973322, '针对IE的XSS过滤10(OWASP TOP 10)', '(?i:<META[ /+\\t].*?http-equiv[ /+\\t]*=[ /+\\t]*[\\\"\\\'`]?(((c|(&#x?0*((67)|(43)|(99)|(63));?)))|((r|(&#x?0*((82)|(52)|(114)|(72));?)))|((s|(&#x?0*((83)|(53)|(115)|(73));?)))))', ' 检测针对IE的如下内容，如： <META http-equiv = ...', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8094, 973324, '针对IE的XSS过滤8(OWASP TOP 10)', '(?i:<EMBED[ /+\\t].*?((src)|(type)).*?=)', ' 检测针对IE的如下内容，如： <EMBED src=....', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8093, 973345, '针对IE的XSS过滤7(OWASP TOP 10)', '(?i:(v|(&#x?0*((86)|(56)|(118)|(76));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(b|(&#x?0*((66)|(42)|(98)|(62));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(s|(&#x?0*((83)|(53)|(115)|(73));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(c|(&#x?0*((67)|(43)|(99)|(63));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(r|(&#x?0*((82)|(52)|(114)|(72));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(i|(&#x?0*((73)|(49)|(105)|(69));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(p|(&#x?0*((80)|(50)|(112)|(70));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(t|(&#x?0*((84)|(54)|(116)|(74));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(:|(&((#x?0*((58)|(3A));?)|(colon;)))).)', ' 检测针对IE内容编码，如：&#x0086、&#x0056;等', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8091, 973326, '针对IE的XSS过滤5(OWASP TOP 10)', '(?i:<.*[:]vmlframe.*?[ /+\\t]*?src[ /+\\t]*=)', ' 检测针对IE的如下内容，如： <:vmlframe src=....', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8092, 973346, '针对IE的XSS过滤6(OWASP TOP 10)', '(?i:(j|(&#x?0*((74)|(4A)|(106)|(6A));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(a|(&#x?0*((65)|(41)|(97)|(61));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(v|(&#x?0*((86)|(56)|(118)|(76));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(a|(&#x?0*((65)|(41)|(97)|(61));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(s|(&#x?0*((83)|(53)|(115)|(73));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(c|(&#x?0*((67)|(43)|(99)|(63));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(r|(&#x?0*((82)|(52)|(114)|(72));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(i|(&#x?0*((73)|(49)|(105)|(69));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(p|(&#x?0*((80)|(50)|(112)|(70));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(t|(&#x?0*((84)|(54)|(116)|(74));?))([\\t]|(&((#x?0*(9|(13)|(10)|A|D);?)|(tab;)|(newline;))))*(:|(&((#x?0*((58)|(3A));?)|(colon;)))).)', ' 检测针对IE内容编码，如：&#x0074、&#x004A;等', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8083, 973311, '检测(88,83,83)(OWASP TOP 10)', '(88,83,83)', ' 检测(88,83,83)，如：String.fromCharCode(88,83,83)', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8084, 973312, '检测可疑符号及xss标签(OWASP TOP 10)', '\'\';!--\\\"<xss>=&{}', ' 检测可疑符号及xss标签，如：\'\';!--\"<XSS>=&{()}', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8085, 973313, '检测&{(OWASP TOP 10)', '&{', ' 检测&{，如：&{alert(\'xss\')}，这个在Netscape 4中会执行', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8086, 973314, '利用<!(doctype|entity)标签的XSS(OWASP TOP 10)', '<!(doctype|entity)', ' 检测可能的利用<!(doctype，<!ENTITY进行的XSS，如：<!DOCTYPE html [  <!ENTITY inject \"&#60;script&#62;alert(1)&#60;/script&#62;\"> ]>', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8087, 973331, '针对IE的XSS过滤1(OWASP TOP 10)', '(?i:<script.*?>)', ' 检测针对IE的如下内容，如： <script ...>...', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8088, 973315, '针对IE的XSS过滤2(OWASP TOP 10)', '(?i:<style.*?>.*?((@[i\\\\\\\\])|(([:=]|(&#x?0*((58)|(3A)|(61)|(3D));?)).*?([(\\\\\\\\]|(&#x?0*((40)|(28)|(92)|(5C));?)))))', ' 检测针对IE的如下内容，如： <style ...>@i...', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8089, 973330, '针对IE的XSS过滤3(OWASP TOP 10)', '(?i:<script.*?[ /+\\t]*?((src)|(xlink:href)|(href))[ /+\\t]*=)', ' 检测针对IE的如下内容，如： <script src=....', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8090, 973327, '针对IE的XSS过滤4(OWASP TOP 10)', '(?i:<[i]?frame.*?[ /+\\t]*?src[ /+\\t]*=)', ' 检测针对IE的如下内容，如： <iframe src=....', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8082, 973310, '检测包含xss的javascript代码或标签等(OWASP TOP 10)', '[/\'\\\"<]xss[/\'\\\">]', ' 检测包含xss的javascript代码或标签等，如：alert(/xss/)', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8081, 973309, '检测<![CDATA[中的可疑行为(OWASP TOP 10)', '<!\\[cdata\\[|\\]\\]>', '检测<![CDATA[中的可能XSS攻击，如：<C><![CDATA[<IMG SRC=\"javas]]><![CDATA[cript:alert(\'XSS\');\">]]></C>', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8079, 973307, 'javascript片段检测(OWASP TOP 10)', '(fromcharcode|alert|eval)\\s*\\(', ' 通过检测javascript程序片段来检测XSS攻击，比如如下片段：alert(String.fromCharCode(88,83,83) window.execScript(\"alert(\'test\');\", \"JavaScript\");...', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8080, 973308, 'css攻击片段检测(OWASP TOP 10)', 'background\\b\\W*?:\\W*?url|background-image\\b\\W*?:|behavior\\b\\W*?:\\W*?url|-moz-binding\\b|@import\\b|expression\\b\\W*?\\(', ' 检测CSS中的XSS攻击片段。如：<div style=\"background-image: url(javascript:...)\">等。', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8078, 973306, '通过style属性来进行的XSS攻击(OWASP TOP 10)', '\\bstyle\\b\\W*?=', ' 检测通过利用style属性来进行的XSS攻击，比较典型的如：<div style=\"background-image: url(javascript:...)\">', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8077, 973305, '变种的（隐蔽的）利用通用URI属性来进行XSS攻击(OWASP TOP 10)', '(asfunction|javascript|vbscript|data|mocha|livescript):', ' 检测一些隐藏的利用通用URI属性来上传数据进行XSS攻击，如：<img src=jaVaScrIpt:...>， <img src=\"jaa&#09;ascript:...\">等', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8074, 973302, '检测application/x-shockwave-flash|image/svg+xml(OWASP TOP 10)', '.+application/x-shockwave-flash|image/svg\\+xml|text/(css|html|ecmascript|javascript|vbscript|x-(javascript|scriptlet|vbscript)).+', ' 通过在请求内容中检测application/x-shockwave-flash、image/svg+xml、text/css、text/javascript等来检测XSS攻击', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8076, 973304, '利用通用URI属性来进行XSS攻击(OWASP TOP 10)', '\\b(background|dynsrc|href|lowsrc|src)\\b\\W*?=', ' 检测利用通用URI属性来上传数据进行XSS攻击，如：<a href=\"javascript:...\">Link</a> ，<img src=javascript:...>等', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8075, 973303, '检测各个事件(OWASP TOP 10)', '\\bon(abort|blur|change|click|dblclick|dragdrop|error|focus|keydown|keypress|keyup|load|mousedown|mousemove|mouseout|mouseover|mouseup|move|readystatechange|reset|resize|select|submit|unload)\\b\\W*?=', ' 通过在请求内容中检测事件处理的名字，来检测xss攻击，如：<body onload=...>    <img src=x onerror=...>等', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8073, 973301, '检测allowscriptaccess、rel=(OWASP TOP 10)', '\\ballowscriptaccess\\b|\\brel\\b\\W*?=', ' 通过在请求内容中检测allowscriptaccess、 rel=来检测XSS攻击', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8072, 973300, 'xss常规异常检测(OWASP TOP 10)', '<(a|abbr|acronym|address|applet|area|audioscope|b|base|basefront|bdo|bgsound|big|blackface|blink|blockquote|body|bq|br|button|caption|center|cite|code|col|colgroup|comment|dd|del|dfn|dir|div|dl|dt|em|embed|fieldset|fn|font|form|frame|frameset|h1|head|hr|html|i|iframe|ilayer|img|input|ins|isindex|kdb|keygen|label|layer|legend|li|limittext|link|listing|map|marquee|menu|meta|multicol|nobr|noembed|noframes|noscript|nosmartquotes|object|ol|optgroup|option|p|param|plaintext|pre|q|rt|ruby|s|samp|script|select|server|shadow|sidebar|small|spacer|span|strike|strong|style|sub|sup|table|tbody|td|textarea|tfoot|th|thead|title|tr|tt|u|ul|var|wbr|xml|xmp)\\W', ' 通过在请求内容中检测address、applet、area、audioscope、basefront等关键词来检测可能的xss攻击', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8071, 958003, '检测.fromcharcode(OWASP TOP 10)', '\\.fromcharcode\\b', ' 检测请求数据中的.fromcharcode关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8059, 958009, '检测@import(OWASP TOP 10)', '\\@import\\b', ' 检测请求数据中的@import关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8060, 958025, '检测lowsrc中是否包含vbscript代码(OWASP TOP 10)', '\\blowsrc\\b\\W*?\\bvbscript:', ' 检测lowsrc中是否包含vbscript代码', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8061, 958413, '检测onload(OWASP TOP 10)', '\\bonload\\b\\W*?\\=', ' 检测请求数据中的onload关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8062, 958051, '检测script标签的开始(OWASP TOP 10)', '\\< ?script\\b', ' 检测请求数据中的<script关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8063, 958420, '检测onresize(OWASP TOP 10)', '\\bonresize\\b\\W*?\\=', ' 检测请求数据中的onresize关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8064, 958407, '检测onclick(OWASP TOP 10)', '\\bonclick\\b\\W*?\\=', ' 检测请求数据中的onclick关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8065, 958056, '检测iframe中的src(OWASP TOP 10)', '\\biframe\\b.{0,100}?\\bsrc\\b', ' 检测iframe中的src', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8066, 958011, '检测background-image(OWASP TOP 10)', '\\bbackground-image:', ' 检测请求数据中的background-image关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8067, 958412, '检测onkeyup(OWASP TOP 10)', '\\bonkeyup\\b\\W*?\\=', ' 检测请求数据中的onkeyup关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8068, 958008, '检测input中的type是否包含image(OWASP TOP 10)', '<input\\b.*?\\btype\\b\\W*?\\bimage\\b', ' 检测input中的type是否包含image', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8069, 958046, '检测url中是否包含shell代码(OWASP TOP 10)', '\\burl\\b\\W*?\\bshell:', ' 检测url中是否包含shell代码', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8070, 958039, '检测type中的text是否包含javascript代码(OWASP TOP 10)', '\\btype\\b\\W*?\\btext\\b\\W*?\\bjavascript\\b', ' 检测type中的text是否包含javascript代码', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8050, 958041, '检测type中的text是否包含vbscript代码(OWASP TOP 10)', '\\btype\\b\\W*?\\btext\\b\\W*?\\bvbscript\\b', ' 检测type中的text是否包含vbscript代码', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8051, 958416, '检测onmouseout(OWASP TOP 10)', '\\bonmouseout\\b\\W*?\\=', ' 检测请求数据中的onmouseout关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8052, 958024, '检测src是否包含shell代码(OWASP TOP 10)', '\\blowsrc\\b\\W*?\\bshell:', ' 检测src是否包含shell代码', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8053, 958059, '检测asfunction(OWASP TOP 10)', '\\basfunction:', ' 检测请求数据中的asfunction关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8054, 958417, '检测onmouseover(OWASP TOP 10)', '\\bonmouseover\\b\\W*?\\=', ' 检测请求数据中的onmouseover关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8055, 958020, '检测href中是否包含vbscript代码(OWASP TOP 10)', '\\bhref\\b\\W*?\\bvbscript:', ' 检测href中是否包含vbscript代码', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8056, 958045, '检测url中是否包含javascript代码(OWASP TOP 10)', '\\burl\\b\\W*?\\bjavascript:', ' 检测url中是否包含javascript代码', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8057, 958004, '检测.innerhtml(OWASP TOP 10)', '\\.innerhtml\\b', ' 检测请求数据中的.innerhtml关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8058, 958421, '检测onselect(OWASP TOP 10)', '\\bonselect\\b\\W*?\\=', ' 检测请求数据中的onselect关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8049, 958030, '检测src中是否是http(OWASP TOP 10)', '\\bsrc\\b\\W*?\\bhttp:', ' 检测src中是否是http', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8048, 958049, '检测meta(OWASP TOP 10)', '\\< ?meta\\b', ' 检测请求数据中的meta关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8046, 958052, '检测alert(OWASP TOP 10)', '\\balert\\b\\W*?\\(', ' 检测请求数据中的alert关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8047, 958037, '检测type中的application是否包含vbscript代码(OWASP TOP 10)', '\\btype\\b\\W*?\\bapplication\\b\\W*?\\bx-vbscript\\b', ' 检测type中的application是否包含vbscript代码', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8043, 958018, '检测href是否包含javascript代码(OWASP TOP 10)', '\\bhref\\b\\W*?\\bjavascript:', ' 检测href是否包含javascript代码', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8044, 958406, '检测onchange(OWASP TOP 10)', '\\bonchange\\b\\W*?\\=', ' 检测请求数据中的onchange关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8045, 958040, '检测type的text中是否包含javascript代码(OWASP TOP 10)', '\\btype\\b\\W*?\\btext\\b\\W*?\\bjscript\\b', ' 检测type的text中是否包含javascript代码', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8042, 958000, '检测.addImport(OWASP TOP 10)', '\\.addimport\\b', ' 检测请求数据中的.addImport关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8030, 958006, '检测body标签的background(OWASP TOP 10)', '<body\\b.*?\\bbackground\\b', ' 检测body标签的background', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8031, 958033, '检测src中是否包含vbscript代码(OWASP TOP 10)', '\\bsrc\\b\\W*?\\bvbscript:', ' 检测src中是否包含vbscript代码', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8032, 958038, '检测type中text中是否包含ecmascript代码(OWASP TOP 10)', '\\btype\\b\\W*?\\btext\\b\\W*?\\becmascript\\b', ' 检测type中text中是否包含ecmascript代码', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8033, 958409, '检测onfocus(OWASP TOP 10)', '\\bonfocus\\b\\W*?\\=', ' 检测请求数据中的onfocus关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8034, 958001, '检测document.cookie(OWASP TOP 10)', '\\bdocument\\b\\s*\\.\\s*\\bcookie\\b', ' 检测请求数据中的document.cookie关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8035, 958005, '检测<![cdata[(OWASP TOP 10)', '\\<\\!\\[cdata\\[', ' 检测请求数据中的<![cdata[关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8036, 958404, '检测onerror(OWASP TOP 10)', '\\bonerror\\b\\W*?\\=', ' 检测请求数据中的onerror关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8037, 958023, '检测lowsrc中是否包含javascript代码(OWASP TOP 10)', '\\blowsrc\\b\\W*?\\bjavascript:', ' 检测lowsrc中是否包含javascript代码', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8038, 958010, '检测activexobject(OWASP TOP 10)', '\\bactivexobject\\b', ' 检测请求数据中的activexobject关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8039, 958411, '检测onkeypress(OWASP TOP 10)', '\\bonkeypress\\b\\W*?\\=', ' 检测请求数据中的onkeypress关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8040, 958422, '检测onsubmit(OWASP TOP 10)', '\\bonsubmit\\b\\W*?\\=', ' 检测请求数据中的onsubmit关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8041, 958036, '检测type中application是否包含x-javascript代码(OWASP TOP 10)', '\\btype\\b\\W*?\\bapplication\\b\\W*?\\bx-javascript\\b', ' 检测type中application是否包含x-javascript代码', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8022, 958410, '检测onkeydown(OWASP TOP 10)', '\\bonkeydown\\b\\W*?\\=', ' 检测请求数据中的onkeydown关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8023, 958415, '检测onmousemove(OWASP TOP 10)', '\\bonmousemove\\b\\W*?\\=', ' 检测请求数据中的onmousemove关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8024, 958022, '检测livescript(OWASP TOP 10)', '\\blivescript:', ' 检测请求数据中的livescript关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8025, 958405, '检测onblur(OWASP TOP 10)', '\\bonblur\\b\\W*?\\=', ' 检测请求数据中的onblur关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8026, 958419, '检测onmove(OWASP TOP 10)', '\\bonmove\\b\\W*?\\=', ' 检测请求数据中的onmove关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8027, 958028, '检测settimeout(OWASP TOP 10)', '\\bsettimeout\\b\\W*?\\(', ' 检测请求数据中的settimeout关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8028, 958057, '检测iframe(OWASP TOP 10)', '\\< ?iframe', ' 检测请求数据中的iframe关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8029, 958031, '检测src中是否包含javascript代码(OWASP TOP 10)', '\\bsrc\\b\\W*?\\bjavascript:', ' 检测src中是否包含javascript代码', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8016, 958012, '检测copyparentfolder(OWASP TOP 10)', '\\bcopyparentfolder\\b', ' 检测请求数据中的copyparentfolder关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8017, 958423, '检测onunload(OWASP TOP 10)', '\\bonunload\\b\\W*?\\=', ' 检测请求数据中的onunload关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8018, 958002, '检测.execscript(OWASP TOP 10)', '\\.execscript\\b', ' 检测请求数据中的.execscript关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8019, 958017, '检测getspecialfolder(OWASP TOP 10)', '\\bgetspecialfolder\\b', ' 检测请求数据中的getspecialfolder关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8020, 958007, '检测boby标签的中的onload(OWASP TOP 10)', '<body\\b.*?\\bonload\\b', ' 检测请求数据boby标签的中的onload关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8021, 958047, '检测url中是否包含vbscript代码(OWASP TOP 10)', '\\burl\\b\\W*?\\bvbscript:', '', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8015, 958408, '检测ondragdrop(OWASP TOP 10)', '\\bondragdrop\\b\\W*?\\=', ' 检测请求数据中的ondragdrop关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8014, 958013, '检测createtextrange(OWASP TOP 10)', '\\bcreatetextrange\\b', ' 检测请求数据中的createtextrange关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8013, 958019, '检测href中中是否包含shell代码(OWASP TOP 10)', '\\bhref\\b\\W*?\\bshell:', '', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8004, 981018, '检测异常分数是否达到', '@eq 0', '', 'XSS', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8005, 958016, '检测getparentfolder(OWASP TOP 10)', '\\bgetparentfolder\\b', ' 检测请求数据中的getparentfolder关键词，包括请求参数和cookie', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8006, 958414, '检测onmousedown(OWASP TOP 10)', '\\bonmousedown\\b\\W*?\\=', ' 检测请求数据中的onmousedown关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8007, 958032, '检测src shell:(OWASP TOP 10)', '\\bsrc\\b\\W*?\\bshell:', ' 检测请求数据中的src shell:关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8008, 958026, '检测mocha(OWASP TOP 10)', '\\bmocha:', ' 检测请求数据中的mocha:关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8009, 958027, '检测onabort(OWASP TOP 10)', '\\bonabort\\b', ' 检测请求数据中的onabort关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8010, 958054, '检测lowsrc http:(OWASP TOP 10)', '\\blowsrc\\b\\W*?\\bhttp:', ' 检测请求数据中的lowsrc http:关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8011, 958418, '检测onmouseup(OWASP TOP 10)', '\\bonmouseup\\b\\W*?\\=', ' 检测请求数据中的onmouseup关键词', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8012, 958034, '检测css expression(expression可以包含js代码, )(OWASP TOP 10)', '\\bstyle\\b\\W*\\=.*bexpression\\b\\W*\\(', 'expression可以包含js代码', 'XSS', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8003, 981136, '常规异常检测', '@pm jscript onsubmit copyparentfolder document javascript meta onchange onmove onkeydown onkeyup activexobject onerror onmouseup ecmascript bexpression onmouseover vbscript: <![cdata[ http: .innerhtml settimeout shell: onabort asfunction: onkeypress onmousedown onclick .fromcharcode background-image: x-javascript ondragdrop onblur mocha: javascript: onfocus lowsrc getparentfolder onresize @import alert script onselect onmouseout application onmousemove background .execscript livescript: vbscript getspecialfolder .addimport iframe onunload createtextrange <input onload', '', 'XSS', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8001, 973337, '基于事件处理的XSS过滤(OWASP TOP 10)', '(?i)([\\s\\\"\'`;\\/0-9\\=]+on\\w+\\s*=)', '基于onload,onerror事件等的XSS,如： <body onload=\"alert(1)\">', 'XSS', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8002, 973338, '基于javascript uri的XSS过滤(OWASP TOP 10)', '(?i)((?:=|U\\s*R\\s*L\\s*\\\\s*[^>]*\\s*S\\s*C\\s*R\\s*I\\s*P\\s*T\\s*:|&colon;|[\\s\\S]allowscriptaccess[\\s\\S]|[\\s\\S]src[\\s\\S]|[\\s\\S]data:text\\/html[\\s\\S]|[\\s\\S]xlink:href[\\s\\S]|[\\s\\S]base64[\\s\\S]|[\\s\\S]xmlns[\\s\\S]|[\\s\\S]xhtml[\\s\\S]|[\\s\\S]style[\\s\\S]|<style[^>]*>[\\s\\S]*?|[\\s\\S]@import[\\s\\S]|<applet[^>]*>[\\s\\S]*?|<meta[^>]*>[\\s\\S]*?|<object[^>]*>[\\s\\S]*?)', ' 基于javascript uri的XSS攻击，如：<p style=\"background:url(javascript:alert(1))\">', 'XSS', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (8000, 973336, '基于script标签的XSS过滤(OWASP TOP 10)', '(?i)(<script[^>]*>[\\s\\S]*?<\\/script[^>]*>|<script[^>]*>[\\s\\S]*?<\\/script[[\\s\\S]]*[\\s\\S]|<script[^>]*>[\\s\\S]*?<\\/script[\\s]*[\\s]|<script[^>]*>[\\s\\S]*?<\\/script|<script[^>]*>[\\s\\S]*?)', 'script标签的过滤，如：<script> alert(1)</script>', 'XSS', 'pass', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 999003, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 999004, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981051, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981052, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 900045, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 900044, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981132, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981131, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 960003, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981142, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 960001, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 960002, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981053, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981110, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981095, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981094, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981097, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981096, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981091, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981090, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981093, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981092, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981099, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981098, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981105, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981104, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981103, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981102, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981101, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981100, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981086, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981087, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981085, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981088, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981089, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981042, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981043, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981037, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981036, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981040, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981041, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981039, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981038, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 900033, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 900034, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 900035, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981177, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981178, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981006, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981007, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981004, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981005, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981003, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981000, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981001, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 950115, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 950103, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981050, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981198, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981199, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 999006, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 999005, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 900041, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 900040, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 900043, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 900042, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 960335, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 960341, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 960342, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 960343, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 960209, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 960208, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 910006, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 910007, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 910008, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 920010, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 920011, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 920012, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 920015, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 920009, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 920017, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 920007, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 920019, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 920005, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 920008, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 920016, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 920018, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981079, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981078, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 920006, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981080, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981081, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 920020, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 960032, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 960038, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 960010, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 960034, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 960035, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981196, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981197, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981190, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981191, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981192, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981193, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981194, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981195, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981189, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981188, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981187, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981020, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981021, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981022, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981204, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981205, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981201, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981202, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981203, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981143, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981145, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981144, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981300, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981317, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 960000, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 990012, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 990901, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 990002, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 990902, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981082, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981176, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981175, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 900047, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981219, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981235, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981237, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981236, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981239, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981238, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981402, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981403, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981400, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981401, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981406, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981407, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981404, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981405, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981222, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981223, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981220, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981221, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981224, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 900046, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 900048, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981185, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981184, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981182, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981181, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981180, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 999008, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 900038, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 900039, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 900036, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 900037, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981134, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981133, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 950923, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 999010, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 999011, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981138, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981139, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981137, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 950020, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981140, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 958297, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 900032, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 920021, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 920023, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 920022, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981200, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981046, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981047, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981044, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981045, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981048, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981049, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981064, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981055, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981054, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981057, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981056, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981059, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981058, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981060, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981061, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981062, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (0, 981063, 'NULL', 'NULL', 'NULL', 'OTHER', 'block', 1, NULL, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (30000, 301200, 'Accept溢出', 'NULL', 'NULL', 'OVERFLOW', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (30001, 301201, 'Accept-Charset溢出', 'NULL', 'NULL', 'OVERFLOW', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (30002, 301202, 'Accept-Encoding溢出', 'NULL', 'NULL', 'OVERFLOW', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (30003, 301203, 'Cookie溢出', 'NULL', 'NULL', 'OVERFLOW', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (30004, 301204, 'Post溢出', 'NULL', 'NULL', 'OVERFLOW', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (30005, 301205, 'URI溢出', 'NULL', 'NULL', 'OVERFLOW', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (30006, 301206, 'Host溢出', 'NULL', 'NULL', 'OVERFLOW', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (30007, 301207, 'Referer溢出', 'NULL', 'NULL', 'OVERFLOW', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (30008, 301208, 'Authorization溢出', 'NULL', 'NULL', 'OVERFLOW', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (30009, 301209, 'Poxy-Authorization溢出', 'NULL', 'NULL', 'OVERFLOW', 'block', 1, 1395124100, NULL);
INSERT INTO `waf`.`t_rules` (`id`, `realid`, `name`, `content`, `desc`, `type`, `action`, `status`, `update_time`, `redirect_id`) VALUES (30010, 301210, 'User-Agent溢出', 'NULL', 'NULL', 'OVERFLOW', 'block', 1, 1395124100, NULL);

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_actioncat`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_actioncat` (`action_id`, `name`, `desc`) VALUES (1, 'allow', '允许访问');
INSERT INTO `waf`.`t_actioncat` (`action_id`, `name`, `desc`) VALUES (2, 'block', '默认动作');
INSERT INTO `waf`.`t_actioncat` (`action_id`, `name`, `desc`) VALUES (3, 'deny', '拒绝访问');
INSERT INTO `waf`.`t_actioncat` (`action_id`, `name`, `desc`) VALUES (4, 'drop', '关闭链接');
INSERT INTO `waf`.`t_actioncat` (`action_id`, `name`, `desc`) VALUES (5, 'pass', '继续处理');
INSERT INTO `waf`.`t_actioncat` (`action_id`, `name`, `desc`) VALUES (6, 'warning', '仅记录');

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_httptypeset`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (1, 'GET', NULL, 1);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (2, 'POST', NULL, 1);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (3, 'HEAD', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (4, 'OPTIONS', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (5, 'DELETE', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (6, 'SEARCH', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (7, 'PROPFIND', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (8, 'CHECKOUT', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (9, 'CHECHIN', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (10, 'MKCOL', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (11, 'PROPPATCH', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (12, 'SHOWMETHOD', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (13, 'TEXTSEARCH', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (14, 'TRACE', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (15, 'COPY', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (16, 'LOCK', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (17, 'LINK', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (18, 'SPACEJUMP', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (19, 'PUT', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (20, 'CONNECT', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (21, 'MOVE', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (22, 'UNLOCK', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (23, 'UNLINK', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (24, 'TRACK', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (25, 'DEBUG', NULL, 0);
INSERT INTO `waf`.`t_httptypeset` (`id`, `name`, `desc`, `selected`) VALUES (26, 'UNKNOWN', NULL, 0);

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_overflowset`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_overflowset` (`id`, `name`, `value`, `status`, `secname`) VALUES (300200, 'Accept', 2048, 1, 'REQUEST_HEADERS:Accept');
INSERT INTO `waf`.`t_overflowset` (`id`, `name`, `value`, `status`, `secname`) VALUES (300201, 'Accept-Charset', 2048, 1, 'REQUEST_HEADERS:Accept-Charset');
INSERT INTO `waf`.`t_overflowset` (`id`, `name`, `value`, `status`, `secname`) VALUES (300202, 'Accept-Encoding', 2048, 1, 'REQUEST_HEADERS:Accept-Encoding');
INSERT INTO `waf`.`t_overflowset` (`id`, `name`, `value`, `status`, `secname`) VALUES (300203, 'Cookie', 32767, 1, 'REQUEST_HEADERS:Cookie');
INSERT INTO `waf`.`t_overflowset` (`id`, `name`, `value`, `status`, `secname`) VALUES (300204, 'Post', 10000000, 1, 'REQUEST_BODY');
INSERT INTO `waf`.`t_overflowset` (`id`, `name`, `value`, `status`, `secname`) VALUES (300205, 'URI', 2048, 1, 'REQUEST_URI');
INSERT INTO `waf`.`t_overflowset` (`id`, `name`, `value`, `status`, `secname`) VALUES (300206, 'Host', 2048, 1, 'REQUEST_HEADERS:Host');
INSERT INTO `waf`.`t_overflowset` (`id`, `name`, `value`, `status`, `secname`) VALUES (300207, 'Referer', 2048, 1, 'REQUEST_HEADERS:Referer');
INSERT INTO `waf`.`t_overflowset` (`id`, `name`, `value`, `status`, `secname`) VALUES (300208, 'Authorization', 2048, 1, 'REQUEST_HEADERS:Authorization');
INSERT INTO `waf`.`t_overflowset` (`id`, `name`, `value`, `status`, `secname`) VALUES (300209, 'Poxy-Authorization', 2048, 1, 'REQUEST_HEADERS:Poxy-Authorization');
INSERT INTO `waf`.`t_overflowset` (`id`, `name`, `value`, `status`, `secname`) VALUES (300210, 'User-Agent', 2048, 1, 'REQUEST_HEADERS:User-Agent');

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_bridge`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_bridge` (`name`, `nics`, `ageingtime`, `stp`, `forwarddelay`, `maxage`, `hellotime`, `level`) VALUES ('br0', 'eth1,eth2', 300, 0, 15, 20, 2, 32767);

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_nicset`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_nicset` (`nic`, `ip`, `mask`, `gateway`, `isstart`, `islink`, `workmode`, `desc`, `brgname`) VALUES ('eth0', '192.168.0.1', '255.255.255.0', NULL, 1, 1, 'full', '管理口', NULL);
INSERT INTO `waf`.`t_nicset` (`nic`, `ip`, `mask`, `gateway`, `isstart`, `islink`, `workmode`, `desc`, `brgname`) VALUES ('eth1', NULL, NULL, NULL, 1, 1, 'full', 'IN', 'br0');
INSERT INTO `waf`.`t_nicset` (`nic`, `ip`, `mask`, `gateway`, `isstart`, `islink`, `workmode`, `desc`, `brgname`) VALUES ('eth2', NULL, NULL, NULL, 1, 1, 'full', 'OUT', 'br0');
INSERT INTO `waf`.`t_nicset` (`nic`, `ip`, `mask`, `gateway`, `isstart`, `islink`, `workmode`, `desc`, `brgname`) VALUES ('eth3', NULL, NULL, NULL, NULL, NULL, NULL, '反向代理口', NULL);
INSERT INTO `waf`.`t_nicset` (`nic`, `ip`, `mask`, `gateway`, `isstart`, `islink`, `workmode`, `desc`, `brgname`) VALUES ('br0', NULL, NULL, NULL, 1, 1, NULL, NULL, NULL);

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_user`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_user` (`id`, `username`, `email`, `password`, `createtime`, `role`, `errors`, `locktime`, `name`, `phone`, `status`) VALUES (1, 'root', 'admin@163.com', 'ab45b530205df9d2a92f612693849c25', '2014-03-10 14:55:38', 0, 0, 0, '', '', 1);
INSERT INTO `waf`.`t_user` (`id`, `username`, `email`, `password`, `createtime`, `role`, `errors`, `locktime`, `name`, `phone`, `status`) VALUES (2, 'admin', '', '86f3059b228c8acf99e69734b6bb32cc', '2014-05-12 15:32:32', 1, 0, 0, '', '', 1);

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_severity`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_severity` (`severity`, `name`, `desc`) VALUES (0, 'EMERGENCY', '紧急');
INSERT INTO `waf`.`t_severity` (`severity`, `name`, `desc`) VALUES (1, 'ALERT', '警报');
INSERT INTO `waf`.`t_severity` (`severity`, `name`, `desc`) VALUES (2, 'CRITICAL', '严重');
INSERT INTO `waf`.`t_severity` (`severity`, `name`, `desc`) VALUES (3, 'ERROR', '错误');
INSERT INTO `waf`.`t_severity` (`severity`, `name`, `desc`) VALUES (4, 'WARNING', '警告');
INSERT INTO `waf`.`t_severity` (`severity`, `name`, `desc`) VALUES (5, 'NOTICE', '通知');
INSERT INTO `waf`.`t_severity` (`severity`, `name`, `desc`) VALUES (6, 'INFO', '信息');
INSERT INTO `waf`.`t_severity` (`severity`, `name`, `desc`) VALUES (7, 'DEBUG', '调试');

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_userconfig`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_userconfig` (`maxError`, `lockTime`) VALUES (5, 15);

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_httprequesttype`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_httprequesttype` (`id`, `name`, `status`) VALUES (1, 'application/x-www-form-urlencoded', 1);
INSERT INTO `waf`.`t_httprequesttype` (`id`, `name`, `status`) VALUES (2, 'multipart/form-data', 1);
INSERT INTO `waf`.`t_httprequesttype` (`id`, `name`, `status`) VALUES (3, 'text/xml', 1);
INSERT INTO `waf`.`t_httprequesttype` (`id`, `name`, `status`) VALUES (4, 'application/xml', 1);
INSERT INTO `waf`.`t_httprequesttype` (`id`, `name`, `status`) VALUES (5, 'application/x-amf', 1);
INSERT INTO `waf`.`t_httprequesttype` (`id`, `name`, `status`) VALUES (6, 'application/json', 1);

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_httpver`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_httpver` (`id`, `name`, `status`) VALUES (1, 'HTTP/0.9', 1);
INSERT INTO `waf`.`t_httpver` (`id`, `name`, `status`) VALUES (2, 'HTTP/1.0', 1);
INSERT INTO `waf`.`t_httpver` (`id`, `name`, `status`) VALUES (3, 'HTTP/1.1', 1);

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_restrictext`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (1, '.asa', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (2, '.asax', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (3, '.ascx', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (4, '.axd', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (5, '.backup', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (6, '.bak', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (7, '.bat', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (8, '.cdx', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (9, '.cer', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (10, '.cfg', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (11, '.cmd', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (12, '.com', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (13, '.config', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (14, '.conf', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (15, '.cs', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (16, '.csproj', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (17, '.csr', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (18, '.dat', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (19, '.db', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (20, '.dbf', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (21, '.dll', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (22, '.dos', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (23, '.htr', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (24, '.htw', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (25, '.ids', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (26, '.idc', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (27, '.idq', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (28, '.inc', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (29, '.ini', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (30, '.key', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (31, '.licx', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (32, '.lnk', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (33, '.log', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (34, '.mdb', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (35, '.old', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (36, '.pass', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (37, '.pdb', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (38, '.pol', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (39, '.printer', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (40, '.pwd', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (41, '.resources', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (42, '.resx', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (43, '.sql', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (44, '.sys', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (45, '.vb', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (46, '.vbs', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (47, '.vbproj', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (48, '.vsdisco', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (49, '.webinfo', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (50, '.xsd', 1);
INSERT INTO `waf`.`t_restrictext` (`id`, `name`, `status`) VALUES (51, '.xsx', 1);

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_restrictheaders`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_restrictheaders` (`id`, `name`, `status`) VALUES (1, 'Proxy-Connection', 1);
INSERT INTO `waf`.`t_restrictheaders` (`id`, `name`, `status`) VALUES (2, 'Lock-Token', 1);
INSERT INTO `waf`.`t_restrictheaders` (`id`, `name`, `status`) VALUES (3, 'Content-Range', 1);
INSERT INTO `waf`.`t_restrictheaders` (`id`, `name`, `status`) VALUES (4, 'Translate', 1);
INSERT INTO `waf`.`t_restrictheaders` (`id`, `name`, `status`) VALUES (5, 'via', 1);
INSERT INTO `waf`.`t_restrictheaders` (`id`, `name`, `status`) VALUES (6, 'if', 1);

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_baseconfig`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_baseconfig` (`wafengine`, `defaultaction`, `ports`, `deploy`) VALUES ('DetectionOnly', 'allow', '80', 'bridge');

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_webguard`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_webguard` (`id`, `url`, `username`, `password`) VALUES (NULL, 'http://', NULL, NULL);

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_rulefiles`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (42, 'experimental_rules/modsecurity_crs_46_scanner_integration.conf', '999003,999004', NULL, 'experimental');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (17, 'optional_rules/modsecurity_crs_11_avs_traffic.conf', NULL, NULL, 'optional');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (33, 'experimental_rules/modsecurity_crs_11_slow_dos_protection.conf', '981051,981052', NULL, 'experimental');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (27, 'optional_rules/modsecurity_crs_49_header_tagging.conf', '900045,900044', NULL, 'optional');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (38, 'experimental_rules/modsecurity_crs_40_appsensor_detection_point_2.9_honeytrap.conf', '981132,981131', NULL, 'experimental');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (41, 'experimental_rules/modsecurity_crs_42_csp_enforcement.conf', '960003,981142,960001,960002', NULL, 'experimental');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (18, 'optional_rules/modsecurity_crs_13_xml_enabler.conf', '981053', 'XML攻击防护', 'optional');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (37, 'experimental_rules/modsecurity_crs_40_appsensor_detection_point_2.1_request_exception.conf', '981110,981095,981094,981097,981096,981091,981090,981093,981092,981099,981098,981105,981104,981103,981102,981101,981100,981086,981087,981085,981088,981089', NULL, 'experimental');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (30, 'experimental_rules/modsecurity_crs_11_brute_force.conf', '981042,981043,981037,981036,981040,981041,981039,981038', NULL, 'experimental');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (43, 'experimental_rules/modsecurity_crs_48_bayes_analysis.conf', '900033,900034,900035', NULL, 'experimental');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (13, 'base_rules/modsecurity_crs_50_outbound.conf', '970118,970018,981177,970003,970011,970010,981178,970012,970015,970014,970016,970002,970021,970008,970009,970903,970902,970901,970007,970004,970904,981006,981007,981004,981005,981003,981000,981001,970013', '程序代码泄漏防护、服务器信息泄漏防护、HTTP错误码防护', 'base');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (8, 'base_rules/modsecurity_crs_41_xss_attacks.conf', '973335,973334,973337,973336,973331,973330,973333,973332,973338,973300,973301,973302,973303,973304,973305,973306,973307,973308,973309,958404,958405,958406,958407,958408,958409,958045,958046,958047,958040,958041,973319,973318,973317,973316,973315,973314,973313,958049,973311,973310,958413,958412,958411,958410,958417,958416,958415,958414,958419,958418,958052,958051,958057,958056,958054,958059,958026,958027,958024,958025,958022,958023,958020,981136,958028,973329,973344,973345,973346,973347,973348,958034,958037,958036,958031,958030,958033,958032,958039,958038,958000,958001,958002,958003,958004,958005,958006,958007,958008,958009,973312,973326,973327,973324,973325,973322,973323,973320,973321,973328,981018,958019,958018,958017,958016,958013,958012,958011,958010,958422,958423,958420,958421', 'XSS跨站脚本防护', 'base');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (25, 'optional_rules/modsecurity_crs_46_av_scanning.conf', '950115', NULL, 'optional');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (9, 'base_rules/modsecurity_crs_42_tight_security.conf', '950103', '目录遍历防护', 'base');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (32, 'experimental_rules/modsecurity_crs_11_proxy_abuse.conf', '981050', NULL, 'experimental');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (45, 'experimental_rules/modsecurity_crs_56_pvi_checks.conf', '981198,981199', NULL, 'experimental');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (39, 'experimental_rules/modsecurity_crs_40_appsensor_detection_point_3.0_end.conf', NULL, NULL, 'experimental');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (34, 'experimental_rules/modsecurity_crs_16_scanner_integration.conf', NULL, NULL, 'experimental');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (16, 'optional_rules/modsecurity_crs_10_ignore_static.conf', '999006,999005,900041,900040,900043,900042', NULL, 'optional');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (3, 'base_rules/modsecurity_crs_23_request_limits.conf', '960335,960341,960342,960343,960209,960208', '溢出攻击防护', 'base');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (29, 'optional_rules/modsecurity_crs_55_marketing.conf', '910006,910007,910008', NULL, 'optional');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (22, 'optional_rules/modsecurity_crs_25_cc_known.conf', '920010,920011,920012,920015,920009,920017,920007,920019,920005,920008,920016,920018,981079,981078,920006,981080,981081,920020', '信用卡信息防护', 'optional');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (4, 'base_rules/modsecurity_crs_30_http_policy.conf', '960032,960038,960010,960034,960035', 'HTTP策略设置', 'base');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (44, 'experimental_rules/modsecurity_crs_55_response_profiling.conf', '981196,981197,981190,981191,981192,981193,981194,981195,981189,981188,981187', NULL, 'experimental');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (11, 'base_rules/modsecurity_crs_47_common_exceptions.conf', '981020,981021,981022', '通用异常防护（APACHE、FLASH等）', 'base');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (15, 'base_rules/modsecurity_crs_60_correlation.conf', '981204,981205,981201,981202,981203', NULL, 'base');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (24, 'optional_rules/modsecurity_crs_43_csrf_protection.conf', '981143,981145,981144', 'CSRF攻击防护', 'optional');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (7, 'base_rules/modsecurity_crs_41_sql_injection_attacks.conf', '959072,959073,959070,959071,981270,981231,950908,981255,981254,981253,981260,981251,981250,950901,981272,981305,981304,981307,981306,981301,981300,981303,981302,981277,981276,981309,981308,981320,981172,950001,950007,981248,981249,981246,981173,981257,981316,981317,981314,981315,981312,981313,981310,981311,981240,981241,981242,981247,981244,981245,981318,981319,981243,981256,981252', 'SQL注入防护', 'base');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (1, 'base_rules/modsecurity_crs_20_protocol_violations.conf', '960018,960911,960016,960912,960915,960914,960012,950801,960022,958231,958230,950107,950109,950108,958291,958295,960020,960901,960902,960000,960011,981227,950116', 'HTTP协议违规防护', 'base');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (5, 'base_rules/modsecurity_crs_35_bad_robots.conf', '990012,990901,990002,990902', '爬虫与扫描攻击防护', 'base');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (10, 'base_rules/modsecurity_crs_45_trojans.conf', '950922,950110,950921', '木马防护', 'base');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (36, 'experimental_rules/modsecurity_crs_40_appsensor_detection_point_2.0_setup.conf', '981082', NULL, 'experimental');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (12, 'base_rules/modsecurity_crs_49_inbound_blocking.conf', '981176,981175', NULL, 'base');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (28, 'optional_rules/modsecurity_crs_55_application_defects.conf', '900047,981219,981235,981237,981236,981239,981238,981402,981403,981400,981401,981406,981407,981404,981405,981222,981223,981220,981221,981224,900046,900048,981185,981184,981182,981181,981180', NULL, 'optional');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (26, 'optional_rules/modsecurity_crs_47_skip_outbound_checks.conf', '999008', NULL, 'optional');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (2, 'base_rules/modsecurity_crs_21_protocol_anomalies.conf', '960021,960009,960008,960015,960017,960007,960006,960904', 'HTTP协议异常防护', 'base');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (46, 'experimental_rules/modsecurity_crs_61_ip_forensics.conf', '900038,900039,900036,900037', NULL, 'experimental');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (21, 'optional_rules/modsecurity_crs_16_username_tracking.conf', NULL, NULL, 'optional');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (6, 'base_rules/modsecurity_crs_40_generic_attacks.conf', '959151,958976,958977,950907,981134,950120,981133,950008,950009,950000,950002,950003,950005,950006,960024,950910,950911,950012,950117,950011,950010,950118,950119,950019,950018', 'LDAP注入防护，命令注入防护、代码注入防护、XML注入防护、EMAIL注入防护、SSI注入防护、UPDF XSS防护、HTTP请求走私防护、HTTP响应分片防护、远程文件包含防护、空字节注入防护', 'base');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (23, 'optional_rules/modsecurity_crs_42_comment_spam.conf', '950923,999010,999011,981138,981139,981137,950020,981140,958297', '垃圾评论防护', 'optional');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (40, 'experimental_rules/modsecurity_crs_40_http_parameter_pollution.conf', '900032', NULL, 'experimental');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (19, 'optional_rules/modsecurity_crs_16_authentication_tracking.conf', NULL, NULL, 'optional');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (35, 'experimental_rules/modsecurity_crs_25_cc_track_pan.conf', '920021,920023,920022', NULL, 'experimental');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (14, 'base_rules/modsecurity_crs_59_outbound_blocking.conf', '981200', NULL, 'base');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (31, 'experimental_rules/modsecurity_crs_11_dos_protection.conf', '981046,981047,981044,981045,981048,981049', NULL, 'experimental');
INSERT INTO `waf`.`t_rulefiles` (`id`, `filename`, `ruleids`, `desc`, `type`) VALUES (20, 'optional_rules/modsecurity_crs_16_session_hijacking.conf', '981064,981055,981054,981057,981056,981059,981058,981060,981061,981062,981063', 'COOKIE防护', 'optional');

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_ruleset`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_ruleset` (`modelname`, `selectedfiles`, `ischecked`) VALUES ('base', '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15', 1);
INSERT INTO `waf`.`t_ruleset` (`modelname`, `selectedfiles`, `ischecked`) VALUES ('optinal', '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,18,20,22,23,24', 0);

COMMIT;


-- -----------------------------------------------------
-- Data for table `waf`.`t_userrole`
-- -----------------------------------------------------
START TRANSACTION;
USE `waf`;
INSERT INTO `waf`.`t_userrole` (`id`, `name`, `roles`) VALUES (1, '系统管理员', '');
INSERT INTO `waf`.`t_userrole` (`id`, `name`, `roles`) VALUES (2, '安全管理员', '');
INSERT INTO `waf`.`t_userrole` (`id`, `name`, `roles`) VALUES (3, '安全审计员', '');

COMMIT;

