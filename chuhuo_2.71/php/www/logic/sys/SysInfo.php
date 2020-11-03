<?php
namespace app\logic\sys;

use Yii;

class SysInfo {
    public $copyRight,//系统版本信息
        $projectName,//项目系统名称
        $timezone,//系统时区
        $systemSessionKey;//系统session key

    public function __construct()
    {
        $sysParams = Yii::$app->sysParams;
        $translate = Yii::$app->sysLanguage;
        $this->copyRight = $translate->getTranslateBySymbol($sysParams->getParamsChild(['systemCopyRight', 'copyRight']));
        #修改copyRight年份
        $this->copyRight = sprintf($this->copyRight, date('Y', time()));
        $this->projectName = $translate->getTranslateBySymbol($sysParams->getParamsChild(['systemCopyRight', 'projectName']));
        $this->timezone = $sysParams->getParamsChild(['systemTimezone']);
        $this->systemSessionKey = $sysParams->getParamsChild(['systemSessionKey']);
    }
}