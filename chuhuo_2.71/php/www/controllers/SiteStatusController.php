<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;

/**
 * 安全管理 - 安全管理 - 可用性监测
 */
class SiteStatusController extends BaseController
{
    public function init()
    {
        parent::init();
        ignore_user_abort(TRUE);
        @set_time_limit(0);
        @ini_set("memory_limit", "256M");
    }

    public function actionIndex()
    {
        $get = Yii::$app->request->get();
        if(isset($get['op']) && 'detail' == $get['op']){
            return ($this->model)::getDetail();
        }
        return parent::actionIndex();
    }

    public function actionView($id)
    {
        return (Yii::$app->request->isAjax) ? ($this->model)::getViewData($id) :
            $this->render('site-view', ['model' => ($this->model)::findOne($id)]);
    }

    public function actionDelete()
    {
        $result = parent::actionDelete();
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        return $result;
    }
}
