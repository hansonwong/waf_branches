<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;

class IntelligentTrojanHorseSet extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['engine'], 'required'],
            [['status', 'maxFileSize', 'updateTime'], 'integer'],
            [['updateTime'], 'filter', 'filter' => function ($value) {
                return time();
            }],
            [['interceptedFileSuffix'], 'safe',],
            [['status'], 'in', 'range' => [0, 1]],
            [['maxFileSize'], 'integer', 'min'=>1, 'max'=>256]
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'engine' => 'engine',
            'status' => 'enable',
            'interceptedFileSuffix' => 'fileSuffixName',
            'maxFileSize' => 'maximumFileAnalysis',
            'updateTime' => 'updateTime',
        ];
    }

    public function returnEngine($type){
        $arr = [
            '1' => Yii::$app->sysLanguage->getTranslateBySymbol('intelligentTrojanHorseSetEngine1'),
        ];
        return AdminListConfig::returnSelect($type, $arr);
    }

    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'updateTime' => ['showType' => 'hidden'],
                'engine' => array_merge($this->returnEngine('select'), [
                    'default' => [
                        'type' => 'callback',
                        'val' => function($obj, $val){
                            return $val ?? 1;
                        },
                    ],
                ]),
                'status' => SelectList::enable('radio'),
                'interceptedFileSuffix' => [
                    'type' => 'multipleVal',
                    'height' => '200px;',
                ],
                'maxFileSize' => ['tips' => Yii::$app->sysLanguage->getTranslateBySymbol('defaultValue').'5M'],
            ],
            'customStr' => false,
        ];
        return $field;
    }

    public function afterSave()
    {
        Yii::$app->wafHelper->pipe("CMD_NGINX");
        return parent::afterSave();
    }
}
