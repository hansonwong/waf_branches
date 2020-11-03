<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;
use app\widget\AdminListConfig;

/**
 * 系统-系统维护 - 配置管理
 * Class BaseConfigController
 * @package app\controllers
 */
class DealConfigController extends BaseController
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
            $downloadPath = Yii::$app->sysPath->downloadPath;
            $realPath = $downloadPath['realPath'];//用于保存到本地
            if( $id == 1 )
            {
                $sFile =$realPath.'/waf_bridge.conf';
                Yii::$app->wafHelper->writeFile('',$sFile);

                Yii::$app->wafHelper->pipe("CMD_SYSTOOL|reset");

                $info = $this->translate->getTranslateBySymbol('restoreConfigurationSuccess');
                AdminListConfig::returnSuccessFieldJson('T', $info, true);
            }
            elseif( $id == 2 )
            {
                $fileName = "bdconfig.dat";
                $sFile =$realPath.'/'.$fileName;
                // 上传文件处理
                $rst =Yii::$app->wafHelper->upFile($sFile);
                if( $rst['code'] != 'T' )
                {
                    AdminListConfig::returnSuccessFieldJson('F', $rst['info'], true);
                }

                Yii::$app->wafHelper->pipe('CMD_SYSCONFIG_RESTORE|/cache/'.$fileName);

                $info = $this->translate->getTranslateBySymbol('uploadSuccessfully').",".$this->translate->getTranslateBySymbol('configurationHasBeenApplied');
                AdminListConfig::returnSuccessFieldJson('T', $info, true);
            }
            elseif( $id == 3 )
            {
                Yii::$app->wafHelper->pipe("CMD_TAR_SYSCONFIG");

                $info = $this->translate->getTranslateBySymbol('generationConfigurationSuccessful');
                AdminListConfig::returnSuccessFieldJson('T', $info, true);
            }
            else
            {
                $info = $this->translate->getTranslateBySymbol('unknownType');
                AdminListConfig::returnSuccessFieldJson('F',$info, true);
            }
        }
        else
        {
            return $this->render('index');
        }

    }
}
