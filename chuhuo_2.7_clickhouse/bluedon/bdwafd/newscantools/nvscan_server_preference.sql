USE waf_hw;

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `nvscan_server_preference`
-- ----------------------------
DROP TABLE IF EXISTS `nvscan_server_preference`;
CREATE TABLE `nvscan_server_preference` (
  `id` int(11) NOT NULL auto_increment,
  `policy_id` int(11) default NULL,
  `name` varchar(40) default NULL,
  `value` varchar(40) default NULL,
  PRIMARY KEY  (`id`),
  KEY `policy_id` (`policy_id`)
) ENGINE=MyISAM AUTO_INCREMENT=65 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of nvscan_server_preference
-- ----------------------------
INSERT INTO `nvscan_server_preference` VALUES ('1', '1', 'throttle_scan', 'yes');
INSERT INTO `nvscan_server_preference` VALUES ('2', '1', 'listen_address', '0.0.0.0');
INSERT INTO `nvscan_server_preference` VALUES ('3', '1', 'slice_network_addresses', 'no');
INSERT INTO `nvscan_server_preference` VALUES ('4', '1', 'non_simult_ports', '139, 445, 3389');
INSERT INTO `nvscan_server_preference` VALUES ('5', '1', 'max_checks', '128');
INSERT INTO `nvscan_server_preference` VALUES ('6', '1', 'stop_scan_on_disconnect', 'yes');
INSERT INTO `nvscan_server_preference` VALUES ('7', '1', 'report_crashes', 'no');
INSERT INTO `nvscan_server_preference` VALUES ('8', '1', 'name', 'all');
INSERT INTO `nvscan_server_preference` VALUES ('9', '1', 'optimize_test', 'yes');
INSERT INTO `nvscan_server_preference` VALUES ('10', '1', 'log_whole_attack', 'no');
INSERT INTO `nvscan_server_preference` VALUES ('11', '1', 'no_target', 'false');
INSERT INTO `nvscan_server_preference` VALUES ('12', '1', 'ssl_cipher_list', 'strong');
INSERT INTO `nvscan_server_preference` VALUES ('13', '1', 'cgi_path', '/cgi-bin:/scripts');
INSERT INTO `nvscan_server_preference` VALUES ('14', '1', 'use_kernel_congestion_detection', 'no');
INSERT INTO `nvscan_server_preference` VALUES ('15', '1', 'listen_port', '4444');
INSERT INTO `nvscan_server_preference` VALUES ('16', '1', 'auto_update', 'no');
INSERT INTO `nvscan_server_preference` VALUES ('17', '1', 'checks_read_timeout', '5');
INSERT INTO `nvscan_server_preference` VALUES ('18', '1', 'plugins_timeout', '60');
INSERT INTO `nvscan_server_preference` VALUES ('19', '1', 'auto_enable_dependencies', 'yes');
INSERT INTO `nvscan_server_preference` VALUES ('20', '1', 'safe_checks', 'yes');
INSERT INTO `nvscan_server_preference` VALUES ('21', '1', 'stop_scan_on_hang', 'yes');
INSERT INTO `nvscan_server_preference` VALUES ('22', '1', 'allow_post_scan_editing', 'yes');
INSERT INTO `nvscan_server_preference` VALUES ('23', '1', 'visibility', 'private');
INSERT INTO `nvscan_server_preference` VALUES ('24', '1', 'wizard_uuid', 'bbd4f805-3966-d464-b2d1-0079eb89d69708c3');
INSERT INTO `nvscan_server_preference` VALUES ('25', '1', 'max_hosts', '20');
INSERT INTO `nvscan_server_preference` VALUES ('26', '1', 'wizard.discovery.discovery type', 'Host enumeration');
INSERT INTO `nvscan_server_preference` VALUES ('27', '1', 'reduce_connections_on_congestion', 'no');
INSERT INTO `nvscan_server_preference` VALUES ('28', '1', 'silent_dependencies', 'yes');
INSERT INTO `nvscan_server_preference` VALUES ('29', '1', 'port_range', 'default');
INSERT INTO `nvscan_server_preference` VALUES ('30', '1', 'feed_type', 'HomeFeed');
INSERT INTO `nvscan_server_preference` VALUES ('31', '1', 'plugin_upload', 'yes');
INSERT INTO `nvscan_server_preference` VALUES ('32', '1', 'xmlrpc_listen_port', '8834');
INSERT INTO `nvscan_server_preference` VALUES ('33', '2', 'throttle_scan', 'yes');
INSERT INTO `nvscan_server_preference` VALUES ('34', '2', 'listen_address', '0.0.0.0');
INSERT INTO `nvscan_server_preference` VALUES ('35', '2', 'slice_network_addresses', 'no');
INSERT INTO `nvscan_server_preference` VALUES ('36', '2', 'non_simult_ports', '139, 445, 3389');
INSERT INTO `nvscan_server_preference` VALUES ('37', '2', 'max_checks', '128');
INSERT INTO `nvscan_server_preference` VALUES ('38', '2', 'stop_scan_on_disconnect', 'yes');
INSERT INTO `nvscan_server_preference` VALUES ('39', '2', 'report_crashes', 'no');
INSERT INTO `nvscan_server_preference` VALUES ('40', '2', 'name', 'all');
INSERT INTO `nvscan_server_preference` VALUES ('41', '2', 'optimize_test', 'yes');
INSERT INTO `nvscan_server_preference` VALUES ('42', '2', 'log_whole_attack', 'no');
INSERT INTO `nvscan_server_preference` VALUES ('43', '2', 'no_target', 'false');
INSERT INTO `nvscan_server_preference` VALUES ('44', '2', 'ssl_cipher_list', 'strong');
INSERT INTO `nvscan_server_preference` VALUES ('45', '2', 'cgi_path', '/cgi-bin:/scripts');
INSERT INTO `nvscan_server_preference` VALUES ('46', '2', 'use_kernel_congestion_detection', 'no');
INSERT INTO `nvscan_server_preference` VALUES ('47', '2', 'listen_port', '4444');
INSERT INTO `nvscan_server_preference` VALUES ('48', '2', 'auto_update', 'no');
INSERT INTO `nvscan_server_preference` VALUES ('49', '2', 'checks_read_timeout', '5');
INSERT INTO `nvscan_server_preference` VALUES ('50', '2', 'plugins_timeout', '60');
INSERT INTO `nvscan_server_preference` VALUES ('51', '2', 'auto_enable_dependencies', 'yes');
INSERT INTO `nvscan_server_preference` VALUES ('52', '2', 'safe_checks', 'yes');
INSERT INTO `nvscan_server_preference` VALUES ('53', '2', 'stop_scan_on_hang', 'yes');
INSERT INTO `nvscan_server_preference` VALUES ('54', '2', 'allow_post_scan_editing', 'yes');
INSERT INTO `nvscan_server_preference` VALUES ('55', '2', 'visibility', 'private');
INSERT INTO `nvscan_server_preference` VALUES ('56', '2', 'wizard_uuid', 'bbd4f805-3966-d464-b2d1-0079eb89d69708c3');
INSERT INTO `nvscan_server_preference` VALUES ('57', '2', 'max_hosts', '20');
INSERT INTO `nvscan_server_preference` VALUES ('58', '2', 'wizard.discovery.discovery type', 'Host enumeration');
INSERT INTO `nvscan_server_preference` VALUES ('59', '2', 'reduce_connections_on_congestion', 'no');
INSERT INTO `nvscan_server_preference` VALUES ('60', '2', 'silent_dependencies', 'yes');
INSERT INTO `nvscan_server_preference` VALUES ('61', '2', 'port_range', 'default');
INSERT INTO `nvscan_server_preference` VALUES ('62', '2', 'feed_type', 'HomeFeed');
INSERT INTO `nvscan_server_preference` VALUES ('63', '2', 'plugin_upload', 'yes');
INSERT INTO `nvscan_server_preference` VALUES ('64', '2', 'xmlrpc_listen_port', '8834');
