<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;

/**
 * 安全管理 - 规则配置 - 自定义规则
 */
class RulesCustomController extends BaseController
{
    public function actionCopyRules(){
        $model = $this->model;
        $model::copyRules();
    }

    public function actionDelete()
    {
        $result = parent::actionDelete();
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        return $result;
    }
}
