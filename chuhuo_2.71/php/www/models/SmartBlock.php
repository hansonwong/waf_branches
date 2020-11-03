<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;

class SmartBlock extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['enable'], 'in', 'range' => [0, 1],],
            [['cycle'], 'filter', 'filter' => function($value){
                return 300;
            }],
            [['invadeCount'], 'integer', 'min' => 10],
            [['standardBlockTime'], 'integer', 'min' => 600],
            [['enable', 'cycle', 'invadeCount', 'standardBlockTime'], 'required'],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => 'smartBlockConfig',
            'enable' => 'enable',
            'cycle' => 'statPeriod',
            'invadeCount' => 'invadeCount',
            'standardBlockTime' => 'standardBlockTime',
        ];
    }

    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'enable' => array_merge(SelectList::enable('select'), ['tipsTKey' => 'smartBlockEnableTips']),
                'cycle' => ['showType' => 'disable', 'tipsTKey' => 'definiteValue300Second'],
                'invadeCount' => ['tipsTKey' => 'allOf10TimeTips'],
                'standardBlockTime' => ['tipsTKey' => 'allOf600TimeTips'],
            ],
        ];
        return $field;
    }
}
