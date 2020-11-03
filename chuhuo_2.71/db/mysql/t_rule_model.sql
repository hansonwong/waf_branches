
ALTER TABLE `waf`.`t_rule_model`
  ADD COLUMN `isDefault` tinyint(3) NOT NULL DEFAULT 0 COMMENT '1为默认预设模板' AFTER `type`;

ALTER TABLE `waf`.`t_rule_model`
  ADD COLUMN `confName` varchar(255) NULL DEFAULT NULL COMMENT 'python那边需要的字段';
  
  
  ALTER TABLE `waf`.`t_rule_model`
  ADD COLUMN `ruleDefault` text NULL COMMENT '这是rule字段的 预设规则ID' AFTER `rule`;