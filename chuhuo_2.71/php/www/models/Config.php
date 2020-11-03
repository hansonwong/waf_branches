<?php

namespace app\models;

use app\widget\AdminListConfig;

class Config extends \app\logic\model\BaseModel
{
    public static function tableName()
    {
        return 'config';
    }

    public function rulesSource()
    {
        return [
            [['symbol'], 'required'],
            [['field_desc', 'json'], 'string'],
            [['symbol', 'desc'], 'string', 'max' => 255],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'symbol' => 'Symbol',
            'desc' => 'Desc',
            'field_desc' => 'Field Desc',
            'json' => 'Json',
        ];
    }

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '~' => ['symbol', 'desc', 'field_desc'],
        ]);
        return ['query' => $query, 'order' => 'symbol'];
    }

    public function ListSearch()
    {
        return [
            'field' => ['symbol', 'desc', 'field_desc'],
            'key' => $this->modelName,
            'model' => $this,
        ];
    }

    public function ListTable()
    {
        return [
            'field' => ['symbol', 'desc', 'field_desc'],
            'model' => $this
        ];
    }

    public function ListField()
    {
        $type = AdminListConfig::ListFieldScenarios('common', $this);
        $fieldKey = $this->modelName;

        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'field_desc'   => ['type' => 'textarea', 'length' => 0, 'height' => '150px'],
                'json'   => ['type' => 'textarea', 'length' => 0, 'height' => '150px'],
            ],
            'customStr' => false,
        ];
        switch ($type) {
            case 'create' :
                break;
            case 'update' :
                break;
            default :
                ;
        }
        return $field;
    }
}
