<?php

namespace app\models;

use Yii;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;

class BaseConfig extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['wafEngine'], 'string', 'max' => 20],
            [['defaultAction'], 'string', 'max' => 10],
            [['ports'], 'string', 'max' => 100],
            [['ports'],'required'],
            [['ports'], function($attribute, $params){
                $val =  explode("|", $this->$attribute);
                $sym = false;

                // 判断检测端口是否为空
                if( empty(array_filter($val,'is_numeric')) ) $sym = true;

                // 判断检测输入端口是否为正整数
                foreach( $val as $v )
                {
                    if( !is_numeric($v) || intval($v)<1 || intval($v)>65535 ) $sym = true;
                }

                if($sym)
                    $this->addError(
                        $attribute,
                        Yii::$app->sysLanguage->getTranslateBySymbol('parameterError')
                    );
            }],
            ['wafEngine', 'in', 'range' => ["On", "Off", "DetectionOnly"], 'message'=>'WAF'.Yii::$app->sysLanguage->getTranslateBySymbol('engineAttrsError')], // WAF引擎参数错误
            ['defaultAction', 'in', 'range' => ["allow", "deny", "drop", "pass"], 'message'=>Yii::$app->sysLanguage->getTranslateBySymbol('nterceptModeAttrsError')], //拦截方式参数错误
            [['deploy', 'blackAndWhite'], 'safe'],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => 'WAF'.Yii::$app->sysLanguage->getTranslateBySymbol('engineConfig'),
            'wafEngine' => 'wafEngine',
            'headTitle2' => 'defaultInterceptModeSetting',
            'defaultAction' => 'interceptionMode',
            'headTitle3' => Yii::$app->sysLanguage->getTranslateBySymbol('baseConfigTestPortSettingsTips').':80|8080',
            'ports' => 'checkPort',
            'deploy' => 'deploymentMode',
            'blackAndWhite' => '',
        ];
    }

    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'deploy' => ['showType' => 'hidden'],
                'blackAndWhite' => ['showType' => 'hidden'],
                'wafEngine' => [
                    'type' => 'radio',#input输入组件类型
                    'data' => [
                        'On' => Yii::$app->sysLanguage->getTranslateBySymbol('open'),
                        'Off' => Yii::$app->sysLanguage->getTranslateBySymbol('close'),
                        'DetectionOnly' => Yii::$app->sysLanguage->getTranslateBySymbol('recordOnly')
                    ],
                    'inputProperty' => 'onchange="showInitForWafEngine()"',
                ],
                'defaultAction' => [
                    'type' => 'radio',#input输入组件类型
                    'data' => SL::actionCatArr(),
                ],
            ],
            'customStr' => \Yii::$app->view->renderFile('@app/views/base-config/config.php'),
        ];
        return $field;
    }

    public function save(){
        $result = parent::save();
        // 端口信息写入文件
        Yii::$app->wafHelper->writeFile($this->ports);

        // 写入命名管道
        Yii::$app->wafHelper->pipe('CMD_PORT');
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        return $result;
    }
}
