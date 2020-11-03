<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;

class PortScanConfig extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['enable', 'status'], 'integer'],
            [['status'], 'filter', 'filter' => function ($value) {
                return 0;
            }],
            [['ip',], 'string', 'max' => 100],
            #[['ip',], \app\logic\validator\IpValidator::className(), 'type' => 'mix', 'typeMix' => ['ip', 'ipIntervalFor4', 'ipWithMask'], 'skipOnEmpty' => false, 'skipOnError' => false],
        ];
    }

    public function save()
    {
        $result = parent::save();
        if($result) Yii::$app->wafHelper->pipe('CMD_PORTSCAN');
        return $result;
    }

    public function attributeLabelsSource()
    {
        return [
            'ip' => 'IP',
            'enable' => 'enable',
            'status' => 'status',
        ];
    }

    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'ip' => ['tipsPsTKey' => ['ruleCustomDefendPolicyIpLimitTips2']],
                'status' => ['showType' => 'hidden'],
                'enable' => SelectList::enable('radio'),
            ],
            'submitArea' => false,
            'customStr' => \Yii::$app->view->renderFile('@app/views/port-scan/edit.php'),
        ];
        return $field;
    }
}
