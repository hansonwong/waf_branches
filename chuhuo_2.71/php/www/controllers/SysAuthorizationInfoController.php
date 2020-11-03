<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;
use app\models\License;
use app\widget\AdminListConfig;

class SysAuthorizationInfoController extends BaseController
{
    /**
     * @return array|string
     * @throws \yii\base\ExitException
     */
	public function actionConfig()
	{
        //判断是不是Ajax提交
        if( Yii::$app->request->isAjax )
        {
            // 许可证文件处理
            $fileName = "license.dat";
            $sFile = Yii::$app->sysPath->cachePath.$fileName;
            // 上传文件处理
            $rst =Yii::$app->wafHelper->upFile($sFile, ["dat"]);
            if( $rst['code'] != 'T' )
            {
                AdminListConfig::returnSuccessFieldJson('F', $rst['info'], true);
            }

            Yii::$app->wafHelper->pipe('CMD_UPDATECERT|' . $sFile);

            // 上传成功,
            $info = Yii::$app->sysLanguage->getTranslateBySymbol("uploadSuccessfully").',';
            // 请耐心等待授权认证
            $info .= Yii::$app->sysLanguage->getTranslateBySymbol("pleaseBePatientWithAuthorizationAuthentication");
            AdminListConfig::returnSuccessFieldJson('T', $info,true);
        }
        else
        {
            $model = License::find()->asArray()->one();
            return $this->render('index',['model'=>$model]);
        }
	}

}