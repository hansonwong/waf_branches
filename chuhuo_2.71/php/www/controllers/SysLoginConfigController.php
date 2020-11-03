<?php

namespace app\controllers;

use Yii;

class SysLoginConfigController extends \app\logic\BaseController{
    public $tabList = [
        [
            'title' => 'loginConfig',
            'default' => true,
            'url' => ['config'],
        ],
        [
            'title' => 'loginPasswordSafePolicy',
            'url' => ['config', 'tab' => 'PassWordPolicy'],
        ],
    ];

    public function actionConfig()
    {
        $get = Yii::$app->request->get();
        $tab = ['PassWordPolicy' => "{$this->modelPrimaryNameSpace}PasswordPolicy"];
        if(isset($get['tab'])) $this->model = $tab[$get['tab']];
        return parent::actionConfig();
    }
}
