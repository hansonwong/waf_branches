<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;
/**
 * 日志管理 -非法外联日志
 */
class OutLinkLogController extends BaseController
{
    public $model = '\\app\\modelLogs\\WeboutLogs';

    /**
     * 添加黑白名单
     */
    public function actionCreate()
    {
        ($this->model)::updateBlackAndWhite();
    }
}
