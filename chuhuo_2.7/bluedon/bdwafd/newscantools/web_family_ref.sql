USE waf_hw;

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `web_family_ref`
-- ----------------------------
DROP TABLE IF EXISTS `web_family_ref`;
CREATE TABLE `web_family_ref` (
  `id` int(11) NOT NULL auto_increment,
  `module` int(11) default NULL,
  `family` int(11) default NULL,
  `vul_id` int(11) default NULL,
  PRIMARY KEY  (`id`),
  KEY `vul_id` (`vul_id`),
  KEY `family` (`family`),
  KEY `module` (`module`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

-- ----------------------------
-- Records of web_family_ref
-- ----------------------------
call create_web_family_ref;

-- ----------------------------
-- Records of web_policy_ref
-- ----------------------------
call create_web_policy;