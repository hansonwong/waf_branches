<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;

class DiskClear extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['enable'], 'in', 'range' => [0, 1],],
            [['limit',], 'integer', 'max' => 100, 'min' => 50],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => 'diskClearAttrs',
            'enable' => 'enable',
            'limit' => 'diskThresholdValue',
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
                'limit' => [
                    'tips' => '% *'.Yii::$app->sysLanguage->getTranslateBySymbol('diskThresholdValueAutoClear'),
                ],
            ],
        ];
        return $field;
    }
}
