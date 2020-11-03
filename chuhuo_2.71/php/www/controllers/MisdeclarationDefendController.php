<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;

/**
 * 安全管理 - 高级设置 - 防误报设置
 */
class MisdeclarationDefendController extends BaseController
{
    public $model = '\\app\\models\\SelfStudyRule';

    public function actionDelete()
    {
        $result = parent::actionDelete();
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        return $result;
    }
}