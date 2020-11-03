USE waf_hw;
SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `user_route`
-- ----------------------------
DROP TABLE IF EXISTS `user_route`;
CREATE TABLE `user_route` (
  `Id` bigint(20) NOT NULL auto_increment,
  `Dest` varchar(20) default NULL,
  `Netmask` varchar(20) default NULL,
  `Gateway` varchar(20) default NULL,
  `Iface` varchar(20) default NULL,
  `Default` tinyint(1) default NULL,
  `Destv6` varchar(45) default NULL,
  `Netmaskv6` varchar(45) default NULL,
  `Gatewayv6` varchar(45) default NULL,
  PRIMARY KEY  (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of user_route
-- ----------------------------
-- INSERT INTO `user_route` VALUES ('1', '0.0.0.0', '0.0.0.0', '192.168.1.1', 'eth2', '1', '', '', '');


-- ----------------------------
-- Table structure for `bridge_config`
-- ----------------------------
DROP TABLE IF EXISTS `bridge_config`;
CREATE TABLE `bridge_config` (
  `Id` bigint(20) NOT NULL auto_increment,
  `Name` varchar(128) character set utf8 default NULL,
  PRIMARY KEY  (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;


-- ----------------------------
-- Table structure for `net_config`
-- ----------------------------
DROP TABLE IF EXISTS `net_config`;
CREATE TABLE `net_config` (
  `Id` smallint(4) NOT NULL auto_increment,
  `Name` varchar(20) NOT NULL,
  `Enable` tinyint(4) default NULL,
  `WorkMode` int(11) NOT NULL,
  `Type` varchar(128) default NULL,
  `BridgeId` int(11) default NULL,
  `Ip` varchar(20) default NULL,
  `Netmask` varchar(20) default NULL,
  `NextHop` varchar(20) default NULL,
  `Gateway` varchar(20) default NULL,
  `Ipv6` varchar(45) default NULL,
  `Netmaskv6` varchar(45) default NULL,
  `NextHopv6` varchar(45) default NULL,
  `Gatewayv6` varchar(45) default NULL,
  PRIMARY KEY  (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of net_config
-- ----------------------------

INSERT INTO `net_config` VALUES ('3', 'eth2', '1', '0', 'DMI|NVS', '0', '192.168.1.10', '255.255.255.0', null, '192.168.1.1','','','','');
INSERT INTO `net_config` VALUES ('4', 'eth3', '1', '1', 'DSI', '0', '192.168.100.1', '255.255.255.0', null, '*','','','','');

-- ----------------------------
-- Sample records of net_config, shell script will use it to insert all the other left NICs. Don't modify except you know exactly.
-- ----------------------------

-- INSERT INTO `net_config` VALUES (0, 'ETH-SAMPLE-NAME', '0', '0', '', '0', '', '', null, '', '', '', '', '');


