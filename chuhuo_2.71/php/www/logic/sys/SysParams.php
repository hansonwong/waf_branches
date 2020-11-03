<?php
namespace app\logic\sys;

use Yii;
class SysParams{
	public static function getParams($key){
		return Yii::$app->params[$key];
	}

	public static function getParamsChild($arr){
		$params = Yii::$app->params;
		$value = $params;
		foreach($arr as $item){
			$value = $value[$item];
		}
		return $value;
	}

	#获取防火墙项目开启状态
	public static function getFirewallSystemStatus(){
	    return self::getParamsChild(['systemFirewall', 'systemEnable']);
    }
}