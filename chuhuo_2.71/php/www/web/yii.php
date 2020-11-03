<?php
if($dev ?? false) {
	error_reporting(E_ALL & ~E_NOTICE & ~E_WARNING);
    defined('YII_DEBUG') or define('YII_DEBUG', true);
    defined('YII_ENV') or define('YII_ENV', 'dev');
} else {
	error_reporting(0);
}
require('../config/init.php');#导入初始化配置
require($frameworkDir . '/vendor/autoload.php');
require($frameworkDir . '/vendor/yiisoft/yii2/Yii.php');
require($frameworkDir . '/common/config/bootstrap.php');
require(__DIR__ . '/../config/bootstrap.php');

$config = yii\helpers\ArrayHelper::merge(
    require($frameworkDir . '/common/config/main.php'),
    #require($frameworkDir . '/common/config/main-local.php'),
    require(__DIR__ . '/../config/main-web.php'),#关于web专属配置
    require(__DIR__ . '/../config/main-local.php'),
    require(__DIR__ . '/../config/main-db.php')
);

$application = new yii\web\Application($config);
$application->run();
