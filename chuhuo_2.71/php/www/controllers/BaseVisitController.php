<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;
use app\logic\waf\models\SelectList;

/**
 * 安全管理 - 规则配置 - 访问控制
 */
class BaseVisitController extends BaseController
{
    public $model = '\\app\\models\\BaseAccessCtrl';

    public function actionDelete()
    {
        $result = parent::actionDelete();
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        return $result;
    }
}
