<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;

/**
 * 安全管理 - 安全管理 - 返回页面设置
 */
class ErrorListController extends BaseController
{
    public function actionDelete()
    {
        ($this->model)::recordDelete();
    }
}