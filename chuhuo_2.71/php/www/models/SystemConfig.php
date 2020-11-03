<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;;

/**
 * This is the model class for table "system_config".
 *
 * @property string $id
 * @property string $config_key
 * @property string $config_value
 * @property string $remark
 */
class SystemConfig extends BaseModel
{
	public static function tableName()
	{
		return 'system_config';
	}

	public function rulesSource()
	{
		return [
			[['config_key', 'config_value'], 'required'],
			[['config_value'], 'string'],
			[['config_key'], 'string', 'max' => 255],
			[['remark'], 'string', 'max' => 100],
			[['config_key'], 'unique'],
		];
	}

	public function attributeLabelsSource()
	{
		return [
			'id' => '主键id',
			'config_key' => '系统配置的键名',
			'config_value' => '系统配置的键值',
			'remark' => '系统配置的描述',
		];
	}

	public function search($params)
	{
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => ['id',],
            '~' => ['config_key', 'config_value', 'remark'],
        ]);
        return ['query' => $query];
	}

	/**
	 * 搜索配置
	 * @return array
	 */
	public function ListSearch()
	{
        return [
            'field' => ['id', 'config_key', 'config_value'],
            'key' => $this->modelName,
            'model' => $this,
        ];
	}

	public function ListTable()
	{
        return [
            'field' => [
                'id' => ['float' => 'r'],
                'config_key',
                'config_value',
                'remark',
            ],
            'model' => $this,
        ];
	}

	/**
	 * 字段修改、添加配置
	 * @return array
	 */
	public function ListField()
	{
		$type = AdminListConfig::ListFieldScenarios('common', $this);
		$fieldKey = $this->modelName;

		switch ($type) {
			case 'create' :
				$field = [
					'fieldKey' => $fieldKey,
					'field' => $this->attributeLabels(),
					'fieldType' => [
					    'id' => ['showType' => 'hidden'],
                    ],
					'customStr' => false,
				];
				break;
			case 'update' :
				$field = [
					'fieldKey' => $fieldKey,
					'field' => $this->attributeLabels(),
                    'fieldType' => [
                        'id' => ['showType' => 'hidden'],
                        'config_key' => ['showType' => 'disable'],
                        'remark' => ['showType' => 'disable'],
                    ],
					'customStr' => false,
				];
				break;
			default :
				;
		}
		return $field;
	}

}
