<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;

/**
 *  日志报表 - 日志 - CC日志
 * Class DdosController
 * @package app\controllers
 */
class CcLogsController extends BaseController
{
    public $modelPrimaryNameSpace = '\\app\\modelLogs\\';

    public function actionIndex()
    {
        $get = Yii::$app->request->get();
        if(isset($get['op']) && 'detail' == $get['op']){
            return ($this->model)::getDetail();
        }
        return parent::actionIndex();
    }
}
