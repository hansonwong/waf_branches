<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;

class MailAlert extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['status','interval', 'phoneStatus'], 'required'],
            [['status','interval', 'phoneStatus'], 'integer'],
            [['status', 'phoneStatus'], 'in', 'range' => [0,1]],
            [['interval'], 'integer', 'max' => 24, 'min' => 1],
            [['now', 'maxValue', 'cycle', 'phoneCycle'], 'safe'],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => 'alertConfig',
            'status' => 'mailAlert',
            'phoneStatus' => 'smsAlert',
            'interval' => 'sendInterval',
            'now' => 'Now',
            'maxValue' => 'Max Value',
            'cycle' => 'Cycle',
            'phoneCycle' => 'Phone Cycle',
        ];
    }

    /**
     * 字段修改、添加配置
     * @return array
     */
    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'status' => array_merge(SelectList::enable('radio'), ['tipsTKey' => 'mailFunForInvadeRecordSwitch']),
                'phoneStatus' => array_merge(SelectList::enable('radio'), ['tipsTKey' => 'smsFunForInvadeRecordSwitch']),
                'interval' => ['tipsTKey' => 'sendIntervalTips'],
                'now' => ['showType' => 'hidden'],
                'maxValue' => ['showType' => 'hidden'],
                'cycle' => ['showType' => 'hidden'],
                'phoneCycle' => ['showType' => 'hidden'],
            ],
        ];
        return $field;
    }
}
