<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;
use app\widget\AdminListConfig;
use app\models\BaseConfig;

#用户管理-接入控制
class SysJoinUpController extends BaseController{
    public $model = '\\app\\models\\BlackAndWhite';

    //改变模式
    public function actionChangeMode($mode){
        $model = new BaseConfig();
        $model->blackAndWhite = $mode;
        $model->save();
        Yii::$app->wafHelper->pipe('CMD_BAW');
        Yii::$app->sysJsonMsg->msg(true, Yii::$app->sysLanguage->getTranslateBySymbol('modifySuccess'));
    }

    public function actionIndex()
    {
        $html = '';
        if(Yii::$app->request->isGet){
            $model = new BaseConfig();
            $html = $this->renderPartial('change-mode', [
                'config' => $model->get(),
            ]);
        }
        return AdminListConfig::showList($this, false, ['header' => $html]);
    }

    public function actionDelete()
    {
        parent::actionDelete();
        Yii::$app->wafHelper->pipe("CMD_BAW");
    }
}
