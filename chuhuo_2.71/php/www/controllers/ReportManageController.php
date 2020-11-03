<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;
class ReportManageController extends BaseController
{
    public function actionReportDownload($id)
    {
        $model = $this->findModel('new', $this->model);
        if($result = $model->getReportFile($id)){
            Yii::$app->sysJsonMsg->data(true, ['file' => $result]);
        }
        Yii::$app->sysJsonMsg->msg(false, Yii::$app->sysLanguage->getTranslateBySymbol('fileDoesNotExist'));
    }
}