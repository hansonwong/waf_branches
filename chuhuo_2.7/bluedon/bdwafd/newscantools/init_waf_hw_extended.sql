-- put vendor specific init waf_hw sql here

USE waf_hw;
SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `user`
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `Id` bigint(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(32) CHARACTER SET utf8 DEFAULT NULL,
  `Password` varchar(32) CHARACTER SET utf8 DEFAULT NULL,
  `Type` int(11) DEFAULT NULL,
  `Maxtasks` int(11) DEFAULT NULL,
  `Iprange` varchar(1024) CHARACTER SET utf8 DEFAULT '*.*.*.*',
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of user
-- ----------------------------
-- user_table_yxlink_style_names
INSERT INTO `user` VALUES ('1', 'sysadmin', '48a365b4ce1e322a55ae9017f3daf0c0', '1', '','');
INSERT INTO `user` VALUES ('2', 'webadmin', 'add6bb58e139be103324d04d82d8f545', '2', '3','*.*.*.*');
INSERT INTO `user` VALUES ('3', 'auditor', 'f7d07071ed9431ecae3a8d45b4c82bb2', '3', '','');
-- user_table_yxlink_style_names


-- ----------------------------
-- Table structure for `user_config`
-- ----------------------------
DROP TABLE IF EXISTS `user_config`;
CREATE TABLE `user_config` (
  `Id` int(11) NOT NULL auto_increment,
  `Name` varchar(255) character set utf8 NOT NULL,
  `Value` text character set utf8,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY  (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
-- ----------------------------
-- Records of user_config
-- ----------------------------
INSERT INTO `user_config` VALUES ('1', 'rfi_url', '', '2');
INSERT INTO `user_config` VALUES ('2', 'rfi_keyword', '', '2');
INSERT INTO `user_config` VALUES ('3', 'domain_ports', '80|81|8000|8080|8088|8090|7001|9080|9090', '2');

-- ----------------------------
-- Table structure for `config`
-- ----------------------------
DROP TABLE IF EXISTS `config`;
CREATE TABLE `config` (
  `Id` bigint(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(128) CHARACTER SET utf8 DEFAULT NULL,
  `Value` varchar(1024) CHARACTER SET utf8 DEFAULT NULL,
  `Type` int(11) DEFAULT NULL,
  `Reboot` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `Name` (`Name`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of config
-- ----------------------------
INSERT INTO `config` VALUES ('1', 'email_from', 'support@test.com', '1', '0');
INSERT INTO `config` VALUES ('2', 'email_account', 'support', '1', '0');
INSERT INTO `config` VALUES ('3', 'email_pass', 'password', '1', '0');
INSERT INTO `config` VALUES ('4', 'email_smtp', 'smtp.test.com', '1', '0');
INSERT INTO `config` VALUES ('5', 'email_smtp_port', '25', '1', '0');
INSERT INTO `config` VALUES ('6', 'email_send_to', 'support@test.com', '1', '0');
INSERT INTO `config` VALUES ('7', 'network_ip', '192.168.1.10', '1', '0');
INSERT INTO `config` VALUES ('8', 'network_gateway', '192.168.1.1', '1', '0');
INSERT INTO `config` VALUES ('9', 'network_subgroup', '255.255.255.0', '1', '0');
INSERT INTO `config` VALUES ('10', 'network_dns1', '8.8.8.8', '1', '0');
INSERT INTO `config` VALUES ('11', 'network_dns2', '', '1', '0');
INSERT INTO `config` VALUES ('12', 'block_type', 'b', '1', '0');
INSERT INTO `config` VALUES ('13', 'block_time', '600', '1', '0');
INSERT INTO `config` VALUES ('14', 'block_ports', '80|8080', '1', '0');
INSERT INTO `config` VALUES ('15', 'maxdisk', '80', '1', '0');
INSERT INTO `config` VALUES ('16', 'productserial', '12345678', '1', '0');
INSERT INTO `config` VALUES ('17', 'enable_senswords', '0', '1', '1');
INSERT INTO `config` VALUES ('18', 'senswords', '法轮功', '1', '1');
INSERT INTO `config` VALUES ('19', 'conntype', 'bridge', '1', '1');
INSERT INTO `config` VALUES ('20', 'log_max_time', '360', '1', '0');
INSERT INTO `config` VALUES ('21', 'prover', '2.6', '1', '0');
INSERT INTO `config` VALUES ('22', 'requestcheck', '', '1', '1');
INSERT INTO `config` VALUES ('23', 'overflow_accept', '2048', '1', '1');
INSERT INTO `config` VALUES ('24', 'overflow_accept_charset', '2048', '1', '1');
INSERT INTO `config` VALUES ('25', 'overflow_accept_encoding', '2048', '1', '1');
INSERT INTO `config` VALUES ('26', 'overflow_authorization', '2048', '1', '1');
INSERT INTO `config` VALUES ('27', 'overflow_cookie', '32767', '1', '1');
INSERT INTO `config` VALUES ('28', 'overflow_host', '2048', '1', '1');
INSERT INTO `config` VALUES ('29', 'overflow_post', '10000000', '1', '1');
INSERT INTO `config` VALUES ('30', 'overflow_proxy_authorization', '2048', '1', '1');
INSERT INTO `config` VALUES ('31', 'overflow_referer', '2048', '1', '1');
INSERT INTO `config` VALUES ('32', 'overflow_url', '2048', '1', '1');
INSERT INTO `config` VALUES ('33', 'overflow_user_agent', '2048', '1', '1');
INSERT INTO `config` VALUES ('34', 'enable_pagestat', '0', '1', '1');
INSERT INTO `config` VALUES ('35', 'loglevel', '30000', '1', '1');
INSERT INTO `config` VALUES ('36', 'bidirection', '0', '1', '1');
INSERT INTO `config` VALUES ('37', 'udpdisable', '0', '1', '1');
INSERT INTO `config` VALUES ('38', 'icmpdisable', '0', '1', '1');
INSERT INTO `config` VALUES ('39', 'rpi_network_ip', '192.168.1.11', '1', '1');
INSERT INTO `config` VALUES ('40', 'rpi_network_gateway', '192.168.1.1', '1', '1');
INSERT INTO `config` VALUES ('41', 'rpi_network_subgroup', '255.255.255.0', '1', '1');
INSERT INTO `config` VALUES ('42', 'rpi_network_dns1', '', '1', '1');
INSERT INTO `config` VALUES ('43', 'rpi_network_dns2', '', '1', '1');
INSERT INTO `config` VALUES ('44', 'enable_senswords_send', '0', '1', '1');
INSERT INTO `config` VALUES ('45', 'senswords_send_ports', '80|8080', '1', '1');
INSERT INTO `config` VALUES ('46', 'enable_senswords_recv', '0', '1', '1');
INSERT INTO `config` VALUES ('47', 'senswords_recv_ports', '80|8080', '1', '1');
INSERT INTO `config` VALUES ('48', 'senswords_send_ports_same', '0', '1', '1');
INSERT INTO `config` VALUES ('49', 'senswords_recv_ports_same', '0', '1', '1');
INSERT INTO `config` VALUES ('50', 'minpasslength', '10', '1', '1');
INSERT INTO `config` VALUES ('51', 'maxloginerror', '3', '1', '1');
INSERT INTO `config` VALUES ('52', 'deploy_type', '1', '1', '1');
INSERT INTO `config` VALUES ('53', 'multi_subnet_protect', '1', '1', '1');
INSERT INTO `config` VALUES ('54', 'unicode_encode_protect', '1', '1', '1');
INSERT INTO `config` VALUES ('55', 'tcp_defragment_protect', '1', '1', '1');
INSERT INTO `config` VALUES ('56', 'tcp_defrag_maxsize', '20', '1', '1');
INSERT INTO `config` VALUES ('57', 'wtfdb_backup_poweron', '0', '1', '1');
INSERT INTO `config` VALUES ('58', 'http_resp_check', '1', '1', '1');
INSERT INTO `config` VALUES ('59', 'cc_ip_check', '0', '1', '1');
INSERT INTO `config` VALUES ('60', 'cc_referer_check', '0', '1', '1');
INSERT INTO `config` VALUES ('61', 'cc_url_ip_check', '0', '1', '1');
INSERT INTO `config` VALUES ('62', 'cc_ip_check_freq', '10', '1', '1');
INSERT INTO `config` VALUES ('63', 'cc_referer_check_freq', '10', '1', '1');
INSERT INTO `config` VALUES ('64', 'cc_url_ip_check_freq', '10', '1', '1');
INSERT INTO `config` VALUES ('65', 'cc_ip_count', '500', '1', '1');
INSERT INTO `config` VALUES ('66', 'cc_referer_count', '500', '1', '1');
INSERT INTO `config` VALUES ('67', 'cc_url_ip_count', '500', '1', '1');
INSERT INTO `config` VALUES ('68', 'cc_block_time', '60', '1', '1');
INSERT INTO `config` VALUES ('69', 'ddos_syn_max', '10000', '1', '1');
INSERT INTO `config` VALUES ('70', 'ddos_ack_max', '10000', '1', '1');
INSERT INTO `config` VALUES ('71', 'ddos_rst_max', '10000', '1', '1');
INSERT INTO `config` VALUES ('72', 'ddos_frag_max', '100', '1', '1');
INSERT INTO `config` VALUES ('73', 'ddos_udp_max', '1000', '1', '1');
INSERT INTO `config` VALUES ('74', 'ddos_icmp_max', '100', '1', '1');
INSERT INTO `config` VALUES ('75', 'ddos_features_enable', '000000', '1', '1');
INSERT INTO `config` VALUES ('76', 'anti_arp_enable', '0', '1', '1');
INSERT INTO `config` VALUES ('77', 'web_accel_enable', '0', '1', '1');
INSERT INTO `config` VALUES ('78', 'vlan_current_mode', '0', '1', '1');
INSERT INTO `config` VALUES ('79', 'vlan_8021q_vid_list', '', '1', '1');
INSERT INTO `config` VALUES ('80', 'vlan_access_vid', '', '1', '1');
INSERT INTO `config` VALUES ('81', 'vlan_8021q_zone', '', '1', '1');
INSERT INTO `config` VALUES ('82', 'ha_enable', '0', '1', '0');
INSERT INTO `config` VALUES ('83', 'ha_local_hostname', 'yxlinknvs', '1', '0');
INSERT INTO `config` VALUES ('84', 'ha_other_hostname', 'yxlinknvs-backup', '1', '0');
INSERT INTO `config` VALUES ('85', 'ha_master_node', '1', '1', '0');
INSERT INTO `config` VALUES ('86', 'ha_line1_ip', '192.168.101.1', '1', '0');
INSERT INTO `config` VALUES ('87', 'ha_line1_subgroup', '255.255.255.0', '1', '0');
INSERT INTO `config` VALUES ('88', 'ha_line1_other_ip', '192.168.101.2', '1', '0');
INSERT INTO `config` VALUES ('89', 'ha_line2_ip', '192.168.102.1', '1', '0');
INSERT INTO `config` VALUES ('90', 'ha_line2_subgroup', '255.255.255.0', '1', '0');
INSERT INTO `config` VALUES ('91', 'ha_line2_other_ip', '192.168.102.2', '1', '0');
INSERT INTO `config` VALUES ('92', 'dhcp_range_start', '192.168.100.10', '1', '0');
INSERT INTO `config` VALUES ('93', 'dhcp_range_end', '192.168.100.100', '1', '0');
INSERT INTO `config` VALUES ('94', 'enable_bonding', '0', '1', '0');
INSERT INTO `config` VALUES ('95', 'bonding_list', '', '1', '0');
INSERT INTO `config` VALUES ('96', 'ha_ipfail_check', '0', '1', '0');
INSERT INTO `config` VALUES ('97', 'ha_ipfail_ip', '', '1', '0');
INSERT INTO `config` VALUES ('98', 'enable_portmirror', '0', '1', '0');
INSERT INTO `config` VALUES ('99', 'urlpattern_candidate_enable', '0', '1', '0');
INSERT INTO `config` VALUES ('100', 'urlpattern_candidate_deadhour', '8', '1', '0');
INSERT INTO `config` VALUES ('101', 'urlpattern_candidate_deadtime', '0', '1', '0');
INSERT INTO `config` VALUES ('102', 'smart_block_enable', '1', '1', '0');
INSERT INTO `config` VALUES ('103', 'smart_block_time', '240', '1', '0');
INSERT INTO `config` VALUES ('104', 'smart_block_count', '5', '1', '0');
INSERT INTO `config` VALUES ('105', 'smart_block_diff_url', '1', '1', '0');
INSERT INTO `config` VALUES ('106', 'smart_block_rule_num', '1', '1', '0');
INSERT INTO `config` VALUES ('107', 'ntp_server1', '210.72.145.44', '1', '0');
INSERT INTO `config` VALUES ('108', 'ntp_server2', '', '1', '0');
INSERT INTO `config` VALUES ('109', 'ntp_server3', '', '1', '0');
INSERT INTO `config` VALUES ('110', 'max_thread', '10', '1', '0');
INSERT INTO `config` VALUES ('111', 'max_task', '10', '1', '0');
INSERT INTO `config` VALUES ('112', 'vpn_ip', '', '1', '0');
INSERT INTO `config` VALUES ('113', 'vpn_username', '', '1', '0');
INSERT INTO `config` VALUES ('114', 'vpn_password', '', '1', '0');

INSERT INTO `config` VALUES ('115', 'syslog_server1', '', '1', '0');
INSERT INTO `config` VALUES ('116', 'syslog_server2', '', '1', '0');
INSERT INTO `config` VALUES ('117', 'syslog_server3', '', '1', '0');

INSERT INTO `config` VALUES ('118', 'socks_enable', '0', '1', '0');
INSERT INTO `config` VALUES ('119', 'socks_port', '', '1', '0');
INSERT INTO `config` VALUES ('120', 'socks_ip', '', '1', '0');
INSERT INTO `config` VALUES ('121', 'socks_username', '', '1', '0');
INSERT INTO `config` VALUES ('122', 'socks_password', '', '1', '0');

INSERT INTO `config` VALUES ('123', 'flowcontrol_enable', '0', '1', '0');
INSERT INTO `config` VALUES ('124', 'flowcontrol_value', '', '1', '0');

INSERT INTO `config` VALUES ('125', 'firewall_enable', '0', '1', '0');
INSERT INTO `config` VALUES ('126', 'firewall_ip', '', '1', '0');
INSERT INTO `config` VALUES ('127', 'firewall_block_time', '60', '1', '0');
INSERT INTO `config` VALUES ('128', 'scan_enable', '0', '1', '0');

INSERT INTO `config` VALUES ('129', 'httpproxy_enable', '0', '1', '0');
INSERT INTO `config` VALUES ('130', 'httpproxy_port', '8080', '1', '0');

INSERT INTO `config` VALUES ('131', 'upgrade_build_site', '', '1', '0');
INSERT INTO `config` VALUES ('132', 'upgrade_build_schedule', '', '1', '0');
INSERT INTO `config` VALUES ('133', 'upgrade_build_mode', '3', '1', '0');
INSERT INTO `config` VALUES ('134', 'upgrade_build_httpproxy_enable', '0', '1', '0');
INSERT INTO `config` VALUES ('135', 'upgrade_build_proxy_site', '', '1', '0');
INSERT INTO `config` VALUES ('136', 'upgrade_build_proxy_port', '8080', '1', '0');
INSERT INTO `config` VALUES ('137', 'upgrade_build_proxy_username', '', '1', '0');
INSERT INTO `config` VALUES ('138', 'upgrade_build_proxy_passwd', '', '1', '0');
INSERT INTO `config` VALUES ('139', 'upgrade_build_end_time', '0000-00-00 00:00:00', '1', '0');

INSERT INTO `config` VALUES ('140', 'upgrade_rules_site', '', '1', '0');
INSERT INTO `config` VALUES ('141', 'upgrade_rules_schedule', '', '1', '0');
INSERT INTO `config` VALUES ('142', 'upgrade_rules_mode', '3', '1', '0');
INSERT INTO `config` VALUES ('143', 'upgrade_rules_httpproxy_enable', '0', '1', '0');
INSERT INTO `config` VALUES ('144', 'upgrade_rules_proxy_site', '', '1', '0');
INSERT INTO `config` VALUES ('145', 'upgrade_rules_proxy_port', '8080', '1', '0');
INSERT INTO `config` VALUES ('146', 'upgrade_rules_proxy_username', '', '1', '0');
INSERT INTO `config` VALUES ('147', 'upgrade_rules_proxy_passwd', '', '1', '0');
INSERT INTO `config` VALUES ('148', 'upgrade_rules_end_time', '0000-00-00 00:00:00', '1', '0');
INSERT INTO `config` VALUES ('149', 'upgrade_package_type_version_md5', '', '1', '0');

INSERT INTO `config` VALUES ('150', 'linkage_waf_enable', '0', '1', '0');
INSERT INTO `config` VALUES ('151', 'linkage_waf_ip', '', '1', '0');
INSERT INTO `config` VALUES ('152', 'linkage_waf_user', '', '1', '0');
INSERT INTO `config` VALUES ('153', 'linkage_waf_pwd', '', '1', '0');

INSERT INTO `config` VALUES ('154', 'vpn_times', '10', '1', '0');

INSERT INTO `config` VALUES ('155', 'httpproxy_flag', '0', '1', '0');

INSERT INTO `config` VALUES ('156', 'network_ipv6_dns1', '', '1', '0');
INSERT INTO `config` VALUES ('157', 'network_ipv6_dns2', '', '1', '0');



-- ----------------------------
-- Table structure for `config_bak`
-- ----------------------------
DROP TABLE IF EXISTS `config_bak`;
CREATE TABLE `config_bak` (
  `Id` bigint(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(128) CHARACTER SET utf8 DEFAULT NULL,
  `Value` varchar(1024) CHARACTER SET utf8 DEFAULT NULL,
  `Type` int(11) DEFAULT NULL,
  `Reboot` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `Name` (`Name`)
) ENGINE=InnoDB  AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of config_bak
-- ----------------------------
INSERT INTO `config_bak` VALUES ('1', 'email_from', 'support@test.com', '1', '0');
INSERT INTO `config_bak` VALUES ('2', 'email_account', 'support', '1', '0');
INSERT INTO `config_bak` VALUES ('3', 'email_pass', 'password', '1', '0');
INSERT INTO `config_bak` VALUES ('4', 'email_smtp', 'smtp.test.com', '1', '0');
INSERT INTO `config_bak` VALUES ('5', 'email_smtp_port', '25', '1', '0');
INSERT INTO `config_bak` VALUES ('6', 'email_send_to', 'support@test.com', '1', '0');
INSERT INTO `config_bak` VALUES ('7', 'network_ip', '192.168.1.10', '1', '0');
INSERT INTO `config_bak` VALUES ('8', 'network_gateway', '192.168.1.1', '1', '0');
INSERT INTO `config_bak` VALUES ('9', 'network_subgroup', '255.255.255.0', '1', '0');
INSERT INTO `config_bak` VALUES ('10', 'network_dns1', '8.8.8.8', '1', '0');
INSERT INTO `config_bak` VALUES ('11', 'network_dns2', '', '1', '0');
INSERT INTO `config_bak` VALUES ('12', 'block_type', 'b', '1', '0');
INSERT INTO `config_bak` VALUES ('13', 'block_time', '600', '1', '0');
INSERT INTO `config_bak` VALUES ('14', 'block_ports', '80|8080', '1', '0');
INSERT INTO `config_bak` VALUES ('15', 'maxdisk', '80', '1', '0');
INSERT INTO `config_bak` VALUES ('16', 'productserial', '12345678', '1', '0');
INSERT INTO `config_bak` VALUES ('17', 'enable_senswords', '0', '1', '1');
INSERT INTO `config_bak` VALUES ('18', 'senswords', '法轮功', '1', '1');
INSERT INTO `config_bak` VALUES ('19', 'conntype', 'bridge', '1', '1');
INSERT INTO `config_bak` VALUES ('20', 'log_max_time', '360', '1', '0');
INSERT INTO `config_bak` VALUES ('21', 'prover', '2.6', '1', '0');
INSERT INTO `config_bak` VALUES ('22', 'requestcheck', '', '1', '1');
INSERT INTO `config_bak` VALUES ('23', 'overflow_accept', '2048', '1', '1');
INSERT INTO `config_bak` VALUES ('24', 'overflow_accept_charset', '2048', '1', '1');
INSERT INTO `config_bak` VALUES ('25', 'overflow_accept_encoding', '2048', '1', '1');
INSERT INTO `config_bak` VALUES ('26', 'overflow_authorization', '2048', '1', '1');
INSERT INTO `config_bak` VALUES ('27', 'overflow_cookie', '32767', '1', '1');
INSERT INTO `config_bak` VALUES ('28', 'overflow_host', '2048', '1', '1');
INSERT INTO `config_bak` VALUES ('29', 'overflow_post', '10000000', '1', '1');
INSERT INTO `config_bak` VALUES ('30', 'overflow_proxy_authorization', '2048', '1', '1');
INSERT INTO `config_bak` VALUES ('31', 'overflow_referer', '2048', '1', '1');
INSERT INTO `config_bak` VALUES ('32', 'overflow_url', '2048', '1', '1');
INSERT INTO `config_bak` VALUES ('33', 'overflow_user_agent', '2048', '1', '1');
INSERT INTO `config_bak` VALUES ('34', 'enable_pagestat', '0', '1', '1');
INSERT INTO `config_bak` VALUES ('35', 'loglevel', '30000', '1', '1');
INSERT INTO `config_bak` VALUES ('36', 'bidirection', '0', '1', '1');
INSERT INTO `config_bak` VALUES ('37', 'udpdisable', '0', '1', '1');
INSERT INTO `config_bak` VALUES ('38', 'icmpdisable', '0', '1', '1');
INSERT INTO `config_bak` VALUES ('39', 'rpi_network_ip', '192.168.1.11', '1', '1');
INSERT INTO `config_bak` VALUES ('40', 'rpi_network_gateway', '192.168.1.1', '1', '1');
INSERT INTO `config_bak` VALUES ('41', 'rpi_network_subgroup', '255.255.255.0', '1', '1');
INSERT INTO `config_bak` VALUES ('42', 'rpi_network_dns1', '', '1', '1');
INSERT INTO `config_bak` VALUES ('43', 'rpi_network_dns2', '', '1', '1');
INSERT INTO `config_bak` VALUES ('44', 'enable_senswords_send', '0', '1', '1');
INSERT INTO `config_bak` VALUES ('45', 'senswords_send_ports', '80|8080', '1', '1');
INSERT INTO `config_bak` VALUES ('46', 'enable_senswords_recv', '0', '1', '1');
INSERT INTO `config_bak` VALUES ('47', 'senswords_recv_ports', '80|8080', '1', '1');
INSERT INTO `config_bak` VALUES ('48', 'senswords_send_ports_same', '0', '1', '1');
INSERT INTO `config_bak` VALUES ('49', 'senswords_recv_ports_same', '0', '1', '1');
INSERT INTO `config_bak` VALUES ('50', 'minpasslength', '10', '1', '1');
INSERT INTO `config_bak` VALUES ('51', 'maxloginerror', '3', '1', '1');
INSERT INTO `config_bak` VALUES ('52', 'deploy_type', '1', '1', '1');
INSERT INTO `config_bak` VALUES ('53', 'multi_subnet_protect', '1', '1', '1');
INSERT INTO `config_bak` VALUES ('54', 'unicode_encode_protect', '1', '1', '1');
INSERT INTO `config_bak` VALUES ('55', 'tcp_defragment_protect', '1', '1', '1');
INSERT INTO `config_bak` VALUES ('56', 'tcp_defrag_maxsize', '20', '1', '1');
INSERT INTO `config_bak` VALUES ('57', 'wtfdb_backup_poweron', '0', '1', '1');
INSERT INTO `config_bak` VALUES ('58', 'http_resp_check', '1', '1', '1');
INSERT INTO `config_bak` VALUES ('59', 'cc_ip_check', '0', '1', '1');
INSERT INTO `config_bak` VALUES ('60', 'cc_referer_check', '0', '1', '1');
INSERT INTO `config_bak` VALUES ('61', 'cc_url_ip_check', '0', '1', '1');
INSERT INTO `config_bak` VALUES ('62', 'cc_ip_check_freq', '10', '1', '1');
INSERT INTO `config_bak` VALUES ('63', 'cc_referer_check_freq', '10', '1', '1');
INSERT INTO `config_bak` VALUES ('64', 'cc_url_ip_check_freq', '10', '1', '1');
INSERT INTO `config_bak` VALUES ('65', 'cc_ip_count', '500', '1', '1');
INSERT INTO `config_bak` VALUES ('66', 'cc_referer_count', '500', '1', '1');
INSERT INTO `config_bak` VALUES ('67', 'cc_url_ip_count', '500', '1', '1');
INSERT INTO `config_bak` VALUES ('68', 'cc_block_time', '60', '1', '1');
INSERT INTO `config_bak` VALUES ('69', 'ddos_syn_max', '10000', '1', '1');
INSERT INTO `config_bak` VALUES ('70', 'ddos_ack_max', '10000', '1', '1');
INSERT INTO `config_bak` VALUES ('71', 'ddos_rst_max', '10000', '1', '1');
INSERT INTO `config_bak` VALUES ('72', 'ddos_frag_max', '100', '1', '1');
INSERT INTO `config_bak` VALUES ('73', 'ddos_udp_max', '1000', '1', '1');
INSERT INTO `config_bak` VALUES ('74', 'ddos_icmp_max', '100', '1', '1');
INSERT INTO `config_bak` VALUES ('75', 'ddos_features_enable', '000000', '1', '1');
INSERT INTO `config_bak` VALUES ('76', 'anti_arp_enable', '0', '1', '1');
INSERT INTO `config_bak` VALUES ('77', 'web_accel_enable', '0', '1', '1');
INSERT INTO `config_bak` VALUES ('78', 'vlan_current_mode', '0', '1', '1');
INSERT INTO `config_bak` VALUES ('79', 'vlan_8021q_vid_list', '', '1', '1');
INSERT INTO `config_bak` VALUES ('80', 'vlan_access_vid', '', '1', '1');
INSERT INTO `config_bak` VALUES ('81', 'vlan_8021q_zone', '', '1', '1');
INSERT INTO `config_bak` VALUES ('82', 'ha_enable', '0', '1', '0');
INSERT INTO `config_bak` VALUES ('83', 'ha_local_hostname', 'yxlinknvs', '1', '0');
INSERT INTO `config_bak` VALUES ('84', 'ha_other_hostname', 'yxlinknvs-backup', '1', '0');
INSERT INTO `config_bak` VALUES ('85', 'ha_master_node', '1', '1', '0');
INSERT INTO `config_bak` VALUES ('86', 'ha_line1_ip', '192.168.101.1', '1', '0');
INSERT INTO `config_bak` VALUES ('87', 'ha_line1_subgroup', '255.255.255.0', '1', '0');
INSERT INTO `config_bak` VALUES ('88', 'ha_line1_other_ip', '192.168.101.2', '1', '0');
INSERT INTO `config_bak` VALUES ('89', 'ha_line2_ip', '192.168.102.1', '1', '0');
INSERT INTO `config_bak` VALUES ('90', 'ha_line2_subgroup', '255.255.255.0', '1', '0');
INSERT INTO `config_bak` VALUES ('91', 'ha_line2_other_ip', '192.168.102.2', '1', '0');
INSERT INTO `config_bak` VALUES ('92', 'dhcp_range_start', '192.168.100.10', '1', '0');
INSERT INTO `config_bak` VALUES ('93', 'dhcp_range_end', '192.168.100.100', '1', '0');
INSERT INTO `config_bak` VALUES ('94', 'enable_bonding', '0', '1', '0');
INSERT INTO `config_bak` VALUES ('95', 'bonding_list', '', '1', '0');
INSERT INTO `config_bak` VALUES ('96', 'ha_ipfail_check', '0', '1', '0');
INSERT INTO `config_bak` VALUES ('97', 'ha_ipfail_ip', '', '1', '0');
INSERT INTO `config_bak` VALUES ('98', 'enable_portmirror', '0', '1', '0');
INSERT INTO `config_bak` VALUES ('99', 'urlpattern_candidate_enable', '0', '1', '0');
INSERT INTO `config_bak` VALUES ('100', 'urlpattern_candidate_deadhour', '8', '1', '0');
INSERT INTO `config_bak` VALUES ('101', 'urlpattern_candidate_deadtime', '0', '1', '0');
INSERT INTO `config_bak` VALUES ('102', 'smart_block_enable', '1', '1', '0');
INSERT INTO `config_bak` VALUES ('103', 'smart_block_time', '240', '1', '0');
INSERT INTO `config_bak` VALUES ('104', 'smart_block_count', '5', '1', '0');
INSERT INTO `config_bak` VALUES ('105', 'smart_block_diff_url', '1', '1', '0');
INSERT INTO `config_bak` VALUES ('106', 'smart_block_rule_num', '1', '1', '0');
INSERT INTO `config_bak` VALUES ('107', 'ntp_server1', '210.72.145.44', '1', '0');
INSERT INTO `config_bak` VALUES ('108', 'ntp_server2', '', '1', '0');
INSERT INTO `config_bak` VALUES ('109', 'ntp_server3', '', '1', '0');
INSERT INTO `config_bak` VALUES ('110', 'max_thread', '10', '1', '0');
INSERT INTO `config_bak` VALUES ('111', 'max_task', '10', '1', '0');
INSERT INTO `config_bak` VALUES ('112', 'vpn_ip', '', '1', '0');
INSERT INTO `config_bak` VALUES ('113', 'vpn_username', '', '1', '0');
INSERT INTO `config_bak` VALUES ('114', 'vpn_password', '', '1', '0');

INSERT INTO `config_bak` VALUES ('115', 'syslog_server1', '', '1', '0');
INSERT INTO `config_bak` VALUES ('116', 'syslog_server2', '', '1', '0');
INSERT INTO `config_bak` VALUES ('117', 'syslog_server3', '', '1', '0');

INSERT INTO `config_bak` VALUES ('118', 'socks_enable', '0', '1', '0');
INSERT INTO `config_bak` VALUES ('119', 'socks_port', '', '1', '0');
INSERT INTO `config_bak` VALUES ('120', 'socks_ip', '', '1', '0');
INSERT INTO `config_bak` VALUES ('121', 'socks_username', '', '1', '0');
INSERT INTO `config_bak` VALUES ('122', 'socks_password', '', '1', '0');

INSERT INTO `config_bak` VALUES ('123', 'flowcontrol_enable', '0', '1', '0');
INSERT INTO `config_bak` VALUES ('124', 'flowcontrol_value', '', '1', '0');

INSERT INTO `config_bak` VALUES ('125', 'firewall_enable', '0', '1', '0');
INSERT INTO `config_bak` VALUES ('126', 'firewall_ip', '', '1', '0');
INSERT INTO `config_bak` VALUES ('127', 'firewall_block_time', '60', '1', '0');
INSERT INTO `config_bak` VALUES ('128', 'scan_enable', '0', '1', '0');

INSERT INTO `config_bak` VALUES ('129', 'httpproxy_enable', '0', '1', '0');
INSERT INTO `config_bak` VALUES ('130', 'httpproxy_port', '8080', '1', '0');

INSERT INTO `config_bak` VALUES ('131', 'upgrade_build_site', '', '1', '0');
INSERT INTO `config_bak` VALUES ('132', 'upgrade_build_schedule', '', '1', '0');
INSERT INTO `config_bak` VALUES ('133', 'upgrade_build_mode', '', '1', '0');
INSERT INTO `config_bak` VALUES ('134', 'upgrade_build_httpproxy_enable', '0', '1', '0');
INSERT INTO `config_bak` VALUES ('135', 'upgrade_build_proxy_site', '', '1', '0');
INSERT INTO `config_bak` VALUES ('136', 'upgrade_build_proxy_port', '8080', '1', '0');
INSERT INTO `config_bak` VALUES ('137', 'upgrade_build_proxy_username', '', '1', '0');
INSERT INTO `config_bak` VALUES ('138', 'upgrade_build_proxy_passwd', '', '1', '0');
INSERT INTO `config_bak` VALUES ('139', 'upgrade_build_end_time', '0000-00-00 00:00:00', '1', '0');

INSERT INTO `config_bak` VALUES ('140', 'upgrade_rules_site', '', '1', '0');
INSERT INTO `config_bak` VALUES ('141', 'upgrade_rules_schedule', '', '1', '0');
INSERT INTO `config_bak` VALUES ('142', 'upgrade_rules_mode', '', '1', '0');
INSERT INTO `config_bak` VALUES ('143', 'upgrade_rules_httpproxy_enable', '0', '1', '0');
INSERT INTO `config_bak` VALUES ('144', 'upgrade_rules_proxy_site', '', '1', '0');
INSERT INTO `config_bak` VALUES ('145', 'upgrade_rules_proxy_port', '8080', '1', '0');
INSERT INTO `config_bak` VALUES ('146', 'upgrade_rules_proxy_username', '', '1', '0');
INSERT INTO `config_bak` VALUES ('147', 'upgrade_rules_proxy_passwd', '', '1', '0');
INSERT INTO `config_bak` VALUES ('148', 'upgrade_rules_end_time', '0000-00-00 00:00:00', '1', '0');
INSERT INTO `config_bak` VALUES ('149', 'upgrade_package_type_version_md5', '', '1', '0');

INSERT INTO `config_bak` VALUES ('150', 'linkage_waf_enable', '0', '1', '0');
INSERT INTO `config_bak` VALUES ('151', 'linkage_waf_ip', '', '1', '0');
INSERT INTO `config_bak` VALUES ('152', 'linkage_waf_user', '', '1', '0');
INSERT INTO `config_bak` VALUES ('153', 'linkage_waf_pwd', '', '1', '0');

INSERT INTO `config_bak` VALUES ('154', 'vpn_times', '10', '1', '0');

INSERT INTO `config_bak` VALUES ('155', 'httpproxy_flag', '0', '1', '0');

INSERT INTO `config_bak` VALUES ('156', 'network_ipv6_dns1', '', '1', '0');
INSERT INTO `config_bak` VALUES ('157', 'network_ipv6_dns2', '', '1', '0');


