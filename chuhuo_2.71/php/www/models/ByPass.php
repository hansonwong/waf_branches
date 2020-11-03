<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;

class ByPass extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['enable'], 'in', 'range' => [0, 1],],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => 'Bypass'.Yii::$app->sysLanguage->getTranslateBySymbol('config'),
            'enable' => 'enable',
        ];
    }

    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'enable' => array_merge(SelectList::enable('radio'), ['tipsPsTKey' => ['bypassOnTips', 'bypassOffTips']])
            ],
            'customStr' => \Yii::$app->view->renderFile('@app/views/base-config/config.php'),
        ];
        return $field;
    }

    public function save(){
        $result = parent::save();
        Yii::$app->wafHelper->pipe("CMD_BYPASS|{$this->enable}");
        return $result;
    }
}
