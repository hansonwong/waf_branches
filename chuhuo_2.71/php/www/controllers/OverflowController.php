<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;
use app\widget\AdminListConfig;
use app\models\OverflowSet;

/**
 * 安全管理 - 高级设置 - HTTP防溢出设置
 */
class OverflowController extends BaseController
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
            $settings = Yii::$app->request->post();
            foreach($settings as $name=>$value)
            {
                if($name == '_csrf') continue;

                $model = OverflowSet::findOne(['name'=>$name]);
                $model->value = $value;
                if( !$model->save() )
                {
                    $info = Yii::$app->wafHelper->getModelErrors($model);
                    AdminListConfig::returnSuccessFieldJson('F',$info,true);
                }
            }

            Yii::$app->wafHelper->pipe("CMD_NGINX");

            $info = Yii::$app->sysLanguage->getTranslateBySymbol('operationSuccess');
            AdminListConfig::returnSuccessFieldJson('T',$info,true);
        }
        else
        {
            $query = OverflowSet::find()->select(['name','value'])->asArray()->all();
            $model = [];
            foreach ($query as $k=>$v)
            {
                $model[$v['name']] = $v['value'];
            }

            return $this->render('index',['model'  => $model]);
        }
	}
}
