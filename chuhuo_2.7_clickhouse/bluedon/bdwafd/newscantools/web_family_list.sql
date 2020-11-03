USE waf_hw;

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `web_family_list`
-- ----------------------------
DROP TABLE IF EXISTS `web_family_list`;
CREATE TABLE `web_family_list` (
  `id` int(11) NOT NULL auto_increment,
  `parent_id` int(11) default '0',
  `desc` varchar(255) character set utf8 default NULL,
  `priority` int(11) default '0',
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=200 DEFAULT CHARSET=latin1;

-- ----------------------------
-- Records of web_family_list
-- ----------------------------
INSERT INTO `web_family_list` VALUES ('1', '194', 'SQL注入', '1');
INSERT INTO `web_family_list` VALUES ('98', '196', '信息泄露', '16');
INSERT INTO `web_family_list` VALUES ('101', '195', '内容电子欺骗', '340');
INSERT INTO `web_family_list` VALUES ('103', '197', '外链信息', '360');
INSERT INTO `web_family_list` VALUES ('108', '198', '弱密码', '4');
INSERT INTO `web_family_list` VALUES ('121', '199', '拒绝服务', '20');
INSERT INTO `web_family_list` VALUES ('122', '196', '目录遍历', '5');
INSERT INTO `web_family_list` VALUES ('123', '194', '系统命令执行', '6');
INSERT INTO `web_family_list` VALUES ('124', '196', '资源位置可预测', '21');
INSERT INTO `web_family_list` VALUES ('125', '198', '越权访问', '7');
INSERT INTO `web_family_list` VALUES ('126', '195', '跨站脚本攻击', '19');
INSERT INTO `web_family_list` VALUES ('127', '198', '逻辑错误', '27');
INSERT INTO `web_family_list` VALUES ('128', '197', '配置不当', '28');
INSERT INTO `web_family_list` VALUES ('194', '0', '命令执行类型', '1');
INSERT INTO `web_family_list` VALUES ('195', '0', '客户端攻击类型', '2');
INSERT INTO `web_family_list` VALUES ('196', '0', '信息泄露类型', '3');
INSERT INTO `web_family_list` VALUES ('197', '0', '其它', '6');
INSERT INTO `web_family_list` VALUES ('198', '0', '认证类型', '4');
INSERT INTO `web_family_list` VALUES ('199', '0', '逻辑攻击类型', '5');

