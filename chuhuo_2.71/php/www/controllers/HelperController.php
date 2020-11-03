<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;

class HelperController extends BaseController{

    //应急支持
    public function actionSos(){
        Yii::$app->wafHelper->sos();
    }
}
