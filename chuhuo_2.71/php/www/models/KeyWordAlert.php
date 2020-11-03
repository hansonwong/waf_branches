<?php
namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;

class KeyWordAlert extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function attributeLabelsSource()
    {
        return [
            'status' => 'open',
            'isBlock' => 'block',
            'urls' => 'defendUrl',
            'exts' => 'fileExtension',
            'words' => 'keywords',
            'maxFileSize' => 'maxFileSize',
            'alertConfig' => 'alertConfig',
        ];
    }

    public function rulesSource()
	{
		return [
            [['maxFileSize'], 'integer'],
            [['alertConfig'], 'string'],
            [['urls', 'exts', 'words', 'status', 'isBlock'], 'safe'],
		];
	}

    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'status' => SelectList::enable('select'),
                'isBlock' => SelectList::enable('select'),
                'urls' => ['type' => 'multipleVal',],
                'exts' => ['type' => 'multipleVal',],
                'words' => ['type' => 'multipleVal',],
            ],
        ];
        return $field;
    }
}
