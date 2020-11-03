<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;

class SensitiveWord extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['enable'], 'in', 'range' => [0, 1],],
            [['words'], 'safe'],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => 'sensitiveWordFilterConfig',
            'enable' => 'enable',
            'words' => 'sensitiveWordContent',
        ];
    }

    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'enable' => SelectList::enable('select'),
                'words' => ['type' => 'multipleVal',],
            ],
        ];
        return $field;
    }

    public function afterSave(){
        Yii::$app->wafHelper->pipe("CMD_NGINX");
    }
}
