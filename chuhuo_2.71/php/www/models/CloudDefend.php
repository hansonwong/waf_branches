<?php

namespace app\models;

use Yii;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;

class CloudDefend extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['init', 'status'], 'string'],
        ];
    }

    public function attributeLabelsSource()
    {
        return [

        ];
    }

    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'init' => ['showType' => 'hidden'],
                'status' => ['showType' => 'hidden'],
            ],
            'customStr' => \Yii::$app->view->renderFile('@app/views/protect/config.php'),
        ];
        return $field;
    }

    public function updateConfig($status){
        $model = new self;
        $model->init = '1';
        $model->status = $status;
        $model->save(false);
    }
}
