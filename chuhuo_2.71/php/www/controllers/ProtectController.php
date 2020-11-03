<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;
use app\models\CcSet;
use app\widget\AdminListConfig;

/**
 * 安全管理 -安全管理 -开启云防护
 */
class ProtectController extends BaseController
{
    public $model = '\\app\\models\\CloudDefend';

	public function actionIndex()
    {
        $model = new $this->model;
        if( Yii::$app->request->get('op')=='updateConfig' ){
            $model->updateConfig(Yii::$app->request->post('status'));
            return 'ok';
        }

        $config = $model->get(true);
        return $this->renderPartial('index', ['config' => $config]);
    }
}
