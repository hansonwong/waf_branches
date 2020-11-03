<?php
return [
    'projectDir' => $projectDir,
	'adminEmail' => 'admin@example.com',
	//iframe下显示子iframe的大小
	//'hui-frame-size' => ['width' => 'maxW', 'height' => 'maxH'],
    'hui-frame-size' => ['width' => '0.75WP', 'height' => '0.85HP'],

	//自动化模型id参数key
	'tableAutoId' => [
		'fetcher' => 'tbFetcherId',
		'auto' => 'tbAutoId',
	],
	//自动化模型配置
	'tableAutoConfig' => [
		'installBase' => [],
		'configTable' => [
			'dbId' => 'dbId', 'tbId' => 'tbId'
		],
	],
	//视图文件指向
	'viewPublicFile' => [
		'public-list' => [
			'common-css' => 'public-list/common-css',
			'common-js' => 'public-list/common-js',
			'table' => 'public-list/public-table',
			'search' => 'public-list/public-search',
			'pagination' => 'public-list/public-pagination',
			'list&config-edit' => 'public-list/public-edit',
		],
		'search-html' => [
			'checkbox-for-id-by-bootstrap-modal' => '/public/search/checkbox-for-id-by-bootstrap-modal',
			'radio-for-id-by-bootstrap-modal' => '/public/search/radio-for-id-by-bootstrap-modal',
			'search-keyword-for-id-by-bootstrap-modal' => '/public/search/search-keyword-for-id-by-bootstrap-modal',
			'search-time-between-by-bootstrap-modal' => '/public/search/search-time-between-by-bootstrap-modal',
			'search-time-by-jquery_ui_datepicker' => '/public/search/search-time-by-jquery_ui_datepicker',
		],
	],
	'holdArgs' => [
		'model' => 'holdModelArgs',
		'common' => 'holdCommonArgs',
	],
];
