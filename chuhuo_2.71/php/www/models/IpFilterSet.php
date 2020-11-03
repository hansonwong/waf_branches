<?php

namespace app\models;

use Yii;
use app\logic\model\tools\SelectList;

class IpFilterSet extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            ['enable', 'in', 'range' => [0, 1]],
            [['ip'], function($attribute, $params){
                $arr = $this->$attribute;
                $ipValidator = new \yii\validators\IpValidator();
                foreach ($arr as $ip){
                    if(strpos($ip,'-') !== false){
                        if(!\app\logic\validator\IpValidator::validateIpIntervalFor4($ip)){
                            $this->addError($attribute, Yii::$app->sysLanguage->getTranslateBySymbol('ipIntervalIsNotLegal'));
                            return;
                        }
                    } elseif($ipValidator->validate($ip, $error));
                    elseif(null != $error){
                        $this->addError($attribute, $error);
                        return;
                    }
                }
            },],
            [['ip',], 'safe'],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => 'ipFilterFitTips',
            'enable' => 'enable',
            'ip' => 'ipFilterOrInterval',
        ];
    }

    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'enable' => array_merge_recursive(SelectList::enable('radio'), ['tipsTKey' => 'ipFilterUseOrNotTips',]),
                'ip' => [
                    'type' => 'multipleVal',
                    'tipsTKey' => 'ipFilterOrIntervalTips',
                    'height' => '200px;',
                ],
            ],
        ];
        return $field;
    }

    public function afterSave(){
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        Yii::$app->wafHelper->pipe( ('1' == $this->enable) ? 'CMD_IPFILTERSET' : 'CMD_IPFILTERSET|EMPTY');
        return true;
    }
}
