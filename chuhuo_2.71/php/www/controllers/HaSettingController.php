<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;
use app\models\BaseConfig;
use app\models\HaSetting;
use app\modelFirewall\Tbnetport;
use app\widget\AdminListConfig;

/**
 * 配置管理 - HA端口及参数配置
 * Class BaseConfigController
 * @package app\controllers
 */
class HaSettingController extends BaseController
{
    /**
     * 列表
     * @return string
     */
	public function actionIndex()
    {
        $model['hasetting'] = HaSetting::findOne(1);
        $model['baseconfig'] = BaseConfig::findOne(1);
        $cond =  ['sPortName' => ['enp8s0', 'enp9s0']];
        $model['nics'] = Tbnetport::find()->where($cond)->orderBy('sPortName')->all();

        $cond = ['like', 'sPortName', 'br'];
        $model['bridge'] = Tbnetport::find()->where($cond)->orderBy('sPortName')->all();

        return $this->render('index', $model);
    }

    /**
     * 更新
     * @param  \app\logic\数据ID $id
     * @return string
     */
    public function actionUpdate($id)
    {
        $model = HaSetting::findOne($id);
        $old_is_use = $model->is_use;
        $old_is_port_aggregation = $model->is_port_aggregation;
        if( $model->load(Yii::$app->request->post()) && $model->save() )
        {
            $post = Yii::$app->request->post();
            $bcof = BaseConfig::findOne($id);
            if($bcof['deploy'] == 'reverseproxy') {
                $cond = ['sPortName' => $post['HaSetting']['interface']];
                $proxynic = Tbnetport::find()->where($cond)->one();
                if($proxynic['sIPV4Address'] == ''){
                    AdminListConfig::returnSuccessFieldJson('F', '选中的接口没有设置IP地址！', false);
                    return;
                }
            }
            // 写入命名管道
            $pcmd = "CMD_UCARP|{$post['HaSetting']['is_use']}|{$old_is_use}|{$post['HaSetting']['is_port_aggregation']}|{$old_is_port_aggregation}";
            //Yii::error( $pcmd);
            Yii::$app->wafHelper->pipe($pcmd);
            $info = $this->translate->getTranslateBySymbol('modifySuccess');
            // 输出json数据
            AdminListConfig::returnSuccessFieldJson('T',$info, false);
        }
        else
        {
            // 获取取检验错误信息
            $info = Yii::$app->wafHelper->getModelErrors($model);
            AdminListConfig::returnSuccessFieldJson('F', $info, false);
        }
    }

}
