<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;

/**
 * 安全管理 -自学习-自学习白名单
 */
class SelfStudyWhiteIpController extends BaseController
{
    public $model = '\\app\\models\\SelfStudyIpWhite';

    public function actionDelete()
    {
        $result = parent::actionDelete();
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        return $result;
    }

}
