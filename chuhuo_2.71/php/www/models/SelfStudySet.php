<?php

namespace app\models;

use Yii;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;

class SelfStudySet extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['isIpBlack', 'isDomainblack'], 'integer'],
            [['isUse', 'isIpWhite','isUseResult'], 'in', 'range' => [0,1]],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => 'selfStudySet',
            'isUse' => 'SelfStudyEnable',
            'isIpWhite' => 'visitWhiteListEnable',
            'isIpBlack' => '',
            'isDomainblack' => '',
            'isUseResult' => 'whetherApplyLearningResults',
        ];
    }

    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'isUse' => array_merge(
                    SelectList::enable('radio'),
                    ['tipsPsTKey' => ['StudyOverLasterClose']]
                ),
                'isIpWhite' => SelectList::enable('radio'),
                'isUseResult' => array_merge(
                    SelectList::enable('radio'),
                    ['tipsPsTKey' => ['StudyOverLasterClose']]
                ),
                'isIpBlack' => ['showType' => 'hidden'],
                'isDomainblack' => ['showType' => 'hidden'],
            ],
        ];
        return $field;
    }

    public function afterSave(){
        Yii::$app->wafHelper->pipe('CMD_NGINX');
    }
}
