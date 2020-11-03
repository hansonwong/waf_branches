<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;

class ServerHeaderHide extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['list'], 'filter', 'filter' => function($value){
                return is_array($value) ? implode('|', $value) : $value;
            }],
            [['list'], 'safe'],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => Yii::$app->sysLanguage->getTranslateBySymbol('openLater').', '.Yii::$app->sysLanguage->getTranslateBySymbol('hideServerHeader'),
            'list' => 'hideType',
        ];
    }

    public function ListField()
    {
        $fileType = ['Server', 'X-Powered-By',];
        $fileTypes = [];
        foreach($fileType as $item){
            $fileTypes[$item] = $item;
        }

        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'list' => [
                    'type' => 'checkbox',
                    'data' => $fileTypes,
                    'labelWidth' => '150px',
                    'rowStyle' => 2,
                    'valSplit' => '|',
                ],
            ],
        ];
        return $field;
    }

    public function afterSave(){
        Yii::$app->wafHelper->pipe("CMD_NGINX");
    }
}
