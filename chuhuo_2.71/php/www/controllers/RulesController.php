<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;

/**
 * 安全管理 - 规则配置 - 内置规则
 */
class RulesController extends BaseController
{
    public function actionIndex()
    {
        $get = Yii::$app->request->get();
        if(isset($get['op']) && 'detail' == $get['op']){
            return ($this->model)::getDetail();
        }
        return parent::actionIndex();
    }

    public function actionUpdate($id = 0){
        $model = $this->model;
        $model::updateStatus();
    }
}
