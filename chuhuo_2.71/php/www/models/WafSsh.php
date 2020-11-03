<?php

namespace app\models;

use Yii;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;

class WafSsh extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['enable'], 'in', 'range' => [0, 1]],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => 'sshSwitchConfig',
            'enable' => 'sshSwitchConfig',
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
            ],
        ];
        return $field;
    }

    public function afterSave(){
        Yii::$app->wafHelper->pipe('CMD_SSH');
    }
}
