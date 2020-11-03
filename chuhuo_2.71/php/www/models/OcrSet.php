<?php

namespace app\models;

use Yii;
use app\logic\model\tools\SelectList;

class OcrSet extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['status', 'websiteId'], 'integer'],
            [['words'], 'required'],
            [['updateTime'], 'safe'],
            [['websiteId'], 'unique'],
            [['urls', 'exts', 'words'], 'safe'],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'status' => 'openState',
            'urls' => 'url',
            'exts' => 'interceptExtensionName',
            'words' => 'extensionName',
            'websiteId' => '',
            'updateTime' => 'updateTime',
        ];
    }

    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'status' => SelectList::enable('radio'),
                'urls' => [
                    'type' => 'multipleVal',
                    'height' => '200px;',
                ],
                'exts' => [
                    'type' => 'multipleVal',
                    'height' => '200px;',
                ],
                'words' => [
                    'type' => 'multipleVal',
                    'height' => '200px;',
                ],
                'websiteId' => ['showType' => 'hidden'],
                'updateTime' => ['showType' => 'hidden'],
            ],
        ];
        return $field;
    }
}
