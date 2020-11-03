<?php
namespace app\logic\waf\wafRules;


class Rules
{
    public static function getDefaultRuleTemplate(){
        $whereStr = "type=3 AND isDefault=1";
        return \app\models\RuleModel::find()->select(['id', 'rule', 'name'])->where($whereStr)->one();
    }
}