<?php
$params = array_merge(
	require($frameworkDir . '/common/config/params.php'),
	//require($frameworkDir . '/common/config/params-local.php'),
	require(__DIR__ . '/params.php'),
	require(__DIR__ . '/params-local.php')
);

return [
	'id' => 'app-frontend',
	'basePath' => $projectDir,
	'bootstrap' => ['log'],
	'runtimePath' => $runtimeDir,
	'controllerNamespace' => 'app\controllers',
	'defaultRoute' => 'index/index',
	'components' => [
		'request' => [
			// !!! insert a secret key in the following (if it is empty) - this is required by cookie validation
			'cookieValidationKey' => 'KYdw8qrVpJAuLCMqjei4H0cu89nFyOmE',
		],
		'user' => [
			'identityClass' => 'app\models\SysUser',
			'enableAutoLogin' => true,
			'identityCookie' => ['name' => '_identity-frontend', 'httpOnly' => true],
		],
		'admin' => [
			'class' => 'yii\web\User',
			'identityClass' => 'app\models\SysUser',
			'enableAutoLogin' => true,
			'identityCookie' => ['name' => '_identity-bluedon', 'httpOnly' => true],
		],
		'session' => [
			// this is the name of the session cookie used for login on the frontend
			'name' => 'advanced-frontend',
		],
		'log' => [
			'traceLevel' => YII_DEBUG ? 3 : 0,
			'targets' => [
				[
					'class' => 'yii\log\FileTarget',
					'levels' => ['error', 'warning'],
				],
			],
		],
		'errorHandler' => [
			'errorAction' => 'site/error',
		],
		'queue' => [
			'class' => 'shmilyzxt\queue\queues\DatabaseQueue', //队列使用的类
			'jobEvent' => [ //队列任务事件配置，目前任务支持2个事件
				'on beforeExecute' => ['shmilyzxt\queue\base\JobEventHandler','beforeExecute'],
				'on beforeDelete' => ['shmilyzxt\queue\base\JobEventHandler','beforeDelete'],
			],
			'connector' => [//队列中间件链接器配置（这是因为使用数据库，所以使用yii\db\Connection作为数据库链接实例）
				'class' => 'yii\db\Connection',
				'dsn' => 'mysql:host=localhost;dbname=tt',
				'username' => 'root',
				'password' => 'root',
				'charset' => 'utf8',
			],
			'table' => 'jobs', //存储队列数据表名
			'queue' => 'default', //队列的名称
			'expire' => 60, //任务过期时间
			'maxJob' =>0, //队列允许最大任务数，0为不限制
			'failed' => [//任务失败日志记录（目前只支持记录到数据库）
				'logFail' => true, //开启任务失败处理
				'provider' => [ //任务失败处理类
					'class' => 'shmilyzxt\queue\failed\DatabaseFailedProvider',
					'db' => [ //数据库链接
						'class' => 'yii\db\Connection',
						'dsn' => 'mysql:host=localhost;dbname=tt',
						'username' => 'root',
						'password' => 'root',
						'charset' => 'utf8',
					],
					'table' => 'failed_jobs' //存储失败日志的表名
				],
			],
		],
		/*
		'urlManager' => [
			'enablePrettyUrl' => true,
			'showScriptName' => false,
			'rules' => [
			],
		],
		*/
	],
	'params' => $params,
];
