<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;

class OutLinkSet extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['enable'], 'in', 'range' => [0, 1],],
            [['dports'], 'string', 'max' => 1024],
            [['dports'], function($attribute, $params){
                $sym = false;
                $ports =  explode("|", $this->$attribute);
                // 判断检测端口是否为空
                if( empty(array_filter($ports,'is_numeric')) ) $sym = true;

                // 判断检测输入端口是否为正整数
                foreach( $ports as $v )
                {
                    if( !is_numeric($v) || intval($v)<1 || intval($v)>65535 ) $sym = true;
                }

                if($sym){
                    $tips = Yii::$app->sysLanguage->getTranslateBySymbol('parameterError'); //'选择了模板类型为站点模板，但没有选择所属站点组模板';
                    $this->addError($attribute, $tips);
                }
            }, 'skipOnEmpty'=>false],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => 'illegalOutLinkSet',
            'enable' => 'enable',
            'dports' => 'checkPort',
        ];
    }

    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'enable' => SelectList::enable('radio'),
                'checkPort' => ['tips' => Yii::$app->sysLanguage->getTranslateBySymbol('OutLinkSetTips').':80|8080'],
            ],
        ];
        return $field;
    }

    public function afterSave(){
        Yii::$app->wafHelper->pipe('CMD_WEBOUTRULE');
    }
}
