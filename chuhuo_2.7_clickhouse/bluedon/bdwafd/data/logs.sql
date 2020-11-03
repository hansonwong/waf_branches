
CREATE DATABASE /*!32312 IF NOT EXISTS*/ `logs` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `logs`;

/* 分表  */
DROP TABLE IF EXISTS `t_website_outbound_log`;
CREATE TABLE IF NOT EXISTS `t_webserver_outbound_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dt` datetime default NULL COMMENT '',
  `sip` varchar(15) DEFAULT '' COMMENT 'source ip',
  `dip` varchar(15) DEFAULT '' COMMENT 'dest ip',
  `sport` varchar(5) DEFAULT '' COMMENT 'source port',
  `dport` varchar(5) DEFAULT '' COMMENT 'dest port',
  `action` tinyint(4) DEFAULT '0' COMMENT '0 1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

