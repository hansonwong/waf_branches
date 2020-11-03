<?php
namespace app\logic\sys;

use Yii;

class SysInit
{
    public function init(){
        self::initSystemDefaultLanguage();
        self::initTimezone();
    }

    //设置系统时区
    public static function initTimezone(){
        date_default_timezone_set(Yii::$app->sysInfo->timezone);
    }

    //设置系统默认语言
    public static function initSystemDefaultLanguage(){
        Yii::$app->sysLanguage->initLanguage();
    }
}