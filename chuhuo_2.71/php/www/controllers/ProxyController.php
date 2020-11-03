<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;

/**
 * 安全管理 - 配置管理 - 反向代理
 */
class ProxyController extends BaseController
{
    public $model = '\\app\\models\\WebSite';

    public function actionIndex()
    {
        if( Yii::$app->request->get('op')=='detail' ) return ($this->model)::getDetail();
        return parent::actionIndex();
    }

    public function actionDelete()
    {
        ($this->model)::recordDelete();
    }
}
