<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;
use app\widget\AdminListConfig;

/**
 * 系统-系统维护 -应急支持
 * Class RefreshZipController
 * @package app\controllers
 */
class RefreshZipController extends BaseController
{
    /**
     * @param int $id
     * @return array|string
     * @throws \yii\base\ExitException
     */
	public function actionConfig($id=0)
    {
        //判断是不是Ajax提交
        if( Yii::$app->request->isAjax )
        {
            Yii::$app->wafHelper->pipe("CMD_TAR_SYSTEMINFO");
            // 输出json数据
            $info = $this->translate->getTranslateBySymbol('modifySuccess');
            AdminListConfig::returnSuccessFieldJson('T', $info, true);
        }
        else
        {
            return $this->render('index');
        }
    }
}
