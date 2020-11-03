<?php

namespace app\controllers;

use Yii;
use app\logic\BaseController;
use app\modelFirewall\TbNetPort;

class ApiCommonController extends BaseController
{

    public $data = ['code' => 'F', 'info' => '', 'data' => ''];

    public function init()
    {
        parent::init();

        Yii::$app->response->format = 'json';
    }

    /**
     * 通过公共接口，获取
     * @throws \yii\base\ExitException
     */
    public function actionGetNetPorts()
    {
        $sPortName = Yii::$app->request->get('sPortName');
        if (strlen($sPortName) < 1)
        {
            $this->data['info'] = $this->translate->getTranslateBySymbol('parameterError'); // 参数错误

            Yii::$app->response->data = $this->data;
            Yii::$app->end();
        }

        // 只支持两个网口查询
        $aPortName = json_decode($sPortName, true);
        if (count($aPortName) !== 2)
        {
            $this->data['info'] = $this->translate->getTranslateBySymbol('parameterError'); // 参数错误

            Yii::$app->response->data = $this->data;
            Yii::$app->end();
        }

        $aPortMode = [];
        foreach ($aPortName as $v)
        {
            $models = TbNetPort::find()->where("sPortName='{$v}'")->asArray()->one();
            if (empty($models))
            {
                $this->data['info'] = $this->translate->getTranslateBySymbol('emptyData'); // 参数错误

                Yii::$app->response->data = $this->data;
                Yii::$app->end();
            }

            $aPortMode[] = $models['sPortMode'];
        }

        $this->data['code'] = 'T';
        $this->data['info'] = $this->translate->getTranslateBySymbol('success');
        $this->data['data'] = $aPortMode;
        Yii::$app->response->data = $this->data;
        Yii::$app->end();

    }
}
