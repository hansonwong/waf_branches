<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;

/**
 * 安全管理 - 规则配置 - 预设规则模板
 */
class RulesDefaultController extends BaseController
{
    //重置模板
    public function actionReset(){
        $model = $this->model;
        $model::reset();
    }
}
