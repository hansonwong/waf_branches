<?php
namespace app\controllers;

use Yii;
use app\widget\AdminListConfig;
use app\logic\BaseController;

class SysLoadMonitoringController extends BaseController
{
    public $layout = 'chart-main';
	public function actionIndex()
	{
        if(Yii::$app->request->isGet){
            return $this->render('/chart-main/sys-load-monitoring');
        }
	}
}
