<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;

/**
 * 安全管理 - 规则配置 - 自定义规则
 */
class RuleCustomDefendPolicyController extends BaseController
{
    public function actionDelete()
    {
        $result = parent::actionDelete();
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        return $result;
    }
}
