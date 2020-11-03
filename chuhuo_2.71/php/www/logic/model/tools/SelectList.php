<?php
namespace app\logic\model\tools;

use Yii;
use app\widget\AdminListConfig;
use app\logic\waf\models\SelectList as SL;

class SelectList
{
    //系统用户组
    public static function systemUserGroup($type, $keyTag = false){
        return AdminListConfig::returnSelect($type, SL::systemUserGroup(), $keyTag);
    }

    //防火墙角色
    public static function systemFirewallUserRole($type, $keyTag = false)
    {
        return AdminListConfig::returnSelect($type, SL::systemFirewallUserRole(), $keyTag);
    }

    //拦截方式
    public static function wafActionCatArr($type, $keyTag = false){
        return AdminListConfig::returnSelect($type, SL::actionCatArr(), $keyTag);
    }

    //危害等级
    public static function wafSeverityArr($type, $keyTag = false){
        return AdminListConfig::returnSelect($type, SL::severityArr(), $keyTag);
    }

    //HTTP请求类型
    public static function wafHttpTypeSetArr($type, $keyTag = false){
        return AdminListConfig::returnSelect($type, SL::httpTypeSetArr(), $keyTag);
    }

    //攻击类别
    public static function wafRuleCatArr($type, $keyTag = false){
        return AdminListConfig::returnSelect($type, SL::ruleCatArr(), $keyTag);
    }

    //内置规则Warn危害级别数组
    public static function ruleWarn($type, $keyTag = false){
        return AdminListConfig::returnSelect($type, SL::ruleWarn(), $keyTag);
    }

    //启用 禁止
    public static function enable($type, $keyTag = false)
    {
        return AdminListConfig::returnSelect($type, SL::enable(), $keyTag);
    }

    //放行 拦截
    public static function passAndIntercept($type, $keyTag = false)
    {
        return AdminListConfig::returnSelect($type, SL::passAndIntercept(), $keyTag);
    }

    //黑白名单
    public static function blackWhiteEnable($type, $keyTag = false)
    {
        return AdminListConfig::returnSelect($type, SL::blackWhiteEnable(), $keyTag);
    }

    //匹配字符算法
    public static function matchingAlgorithmForStr($type, $keyTag = false){
        return AdminListConfig::returnSelect($type, SL::matchingAlgorithmForStr(), $keyTag);
    }

    //文件扩展名
    public static function fileExtension($type, $keyTag = false)
    {
        return AdminListConfig::returnSelect($type, SL::fileExtension(), $keyTag);
    }

    //HTTP请求动作
    public static function httpTypeSet($type, $keyTag = false)
    {
        return AdminListConfig::returnSelect($type, SL::httpTypeSet(), $keyTag);
    }

    //HTTP请求内容
    public static function httpRequestType($type, $keyTag = false)
    {
        return AdminListConfig::returnSelect($type, SL::httpRequestType(), $keyTag);
    }

    //HTTP头字段
    public static function restrictHeaders($type, $keyTag = false)
    {
        return AdminListConfig::returnSelect($type, SL::restrictHeaders(), $keyTag);
    }

    //HTTP协议版本
    public static function httpVersion($type, $keyTag = false)
    {
        return AdminListConfig::returnSelect($type, SL::httpVersion(), $keyTag);
    }

    //规则模板
    public static function rulesSet($type, $keyTag = false){
        return AdminListConfig::returnSelect($type, SL::rulesSet(), $keyTag);
    }

    //规则模板模板类型
    public static function ruleModelTplType($type, $keyTag = false){
        return AdminListConfig::returnSelect($type, SL::ruleModelTplType(), $keyTag);
    }

    //规则模板继承模板
    public static function ruleModelGroup($type, $keyTag = false){
        return AdminListConfig::returnSelect($type, SL::ruleModelGroup(), $keyTag);
    }

    //系统语言
    public static function systemDefaultLanguage($type, $keyTag = false)
    {
        return AdminListConfig::returnSelect($type, SL::systemDefaultLanguage(), $keyTag);
    }
}