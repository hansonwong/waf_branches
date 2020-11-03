<?php
namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;;

class FetchTaskItem extends BaseModel
{
	public static function tableName()
	{
		return 'fetch_task_item';
	}

	public function rulesSource()
	{
		return [
			[['id', 'task_id', 'parent_id'], 'integer'],
			[['tb_create', 'field', 'field_global_var', 'field_attribute_label', 'field_attribute_labels_config', 'field_rules', 'field_search', 'field_search_box', 'field_table', 'field_edit', 'field_data'], 'string'],
			[['title', 'tb'], 'string', 'max' => 100],
		];
	}

	public function attributeLabelsSource()
	{
		return [
			'id' => 'ID',
			'task_id' => 'Task ID',
			'parent_id' => 'Parent ID',
			'title' => 'Title',
			'tb' => 'Tb',
			'tb_create' => 'Tb Create',
			'field' => 'Field',
			'field_global_var' => 'Field Global Var',
			'field_attribute_label' => 'Field Attribute Label',
			'field_attribute_labels_config' => 'Field Attribute Labels Config',
			'field_rules' => 'Field Rules',
			'field_search' => 'Field Search',
			'field_search_box' => 'Field Search Box',
			'field_table' => 'Field Table',
			'field_edit' => 'Field Edit',
			'field_data' => 'Field Data',
		];
	}

	public function attributeLabelsConfig()
	{
		return [
			'field' => ['tips' => "例：id,name,age"],
			'field_global_var' => ['tips' => "例：\$globalVar = [<br>
				'selectByArr' => [<br>
					'isEnable' => ['22' => '22', '33' => '33'],<br>
					'isAllow' => ['0' => '否', '1' => '是'],<br>
				],<br>
				'selectByModel' => [<br>
					'isEnable' => ['modelId' => 1, 'condition' => [], 'type' => 'select', 'key-val' => 'id:name'],<br>
					'isEnableSwitch' => ['modelId' => 3, 'condition' => [], 'type' => 'switch', 'key-val' => 'id:name'],<br>
					'isAllow' => ['modelId' => 1, 'condition' => [], 'type' => 'select', 'key-val' => 'id:name'],<br>
				],<br>
				'magicGetModel' => [<br>
					'ageName' => ['modelId' => 3, 'relation' => ['selfField' => 'group_id', 'relField' => 'id', 'has' => 'one']],<br>
				],<br>
				'searchBy' => [<br>
					'self' => ['fix' => ['id' => 1]],<br>
					'other' => [<br>
						'3' => [<br>
							//'fix' => ['id' => 2],<br>
							'selfField' => [<br>
								//'搜索模式' => ['外表字段' => '本表字段'],<br>
								//'eq' => ['id' => 'name'],<br>
								//'between' => ['id' => 'name'],<br>
								//'like' => ['name' => 'name'],<br>
							],<br>
							'customField' => [<br>
								//'eq' => ['name' => 'age_name'],<br>
								//'between' => ['id' => 'age_name'],<br>
								//'like' => ['name' => 'age_name'],<br>
							],<br>
						],<br>
					],<br>
				],<br>
			];"],
			'field_attribute_label' => ['tips' => "例：\$result = [<br>
				'id' => 'ID',<br>
				'name' => '名字',<br>
				'age' => '年龄',<br>
			];"],
			'field_attribute_labels_config' => [
				'tips' => "例：\$result = [<br>
				'name' => ['tips' => '最少6位英文字符'],<br>
				'age' => ['tips' => '少于100的整数'],<br>
			];"],
			'field_rules' => ['tips' => "例：\$result = [<br>
				[['id', 'age'], 'integer'],<br>
				[['name'], 'string'],<br>
				[['name'], 'string', 'max' => 30],<br>
			];"],
			'field_search' => ['tips' => "\$searchSet = [<br>
				'eq' => ['id'],<br>
				'like' => ['name', 'address'],<br>
				'betweenNum' => ['age'],<br>
				'betweenTime' => [],<br>
			];"],
			'field_search_box' => ['tips' => "\$searchSet = [<br>
				'id', 'name',<br>
				'isAllow' => ['select', ['0' => 'NO', '1' => 'YES']],<br>
				'isEnable' => \$this->returnSelectByArr('select', self::\$globalVar['isEnable']),<br>
				'age' => \$this->returnSelectByArr('select', self::\$globalVar['selectByArr']['isEnable']),<br>
				'age2' => \$this->returnSelectByModel(self::\$globalVar['selectByModel']['isEnable']),<br>
			];<br>
			\$customHtml = [<br>
				'search-time-between' => [<br>
					//['field' => 'age', 'label' => 'AGE'],<br>
				],<br>
				'search-time' => ['age'],<br>
				'search-keyword-for-id' => [<br>
					//['field' => 'age', 'urlArgs' => ['tbFetcherId' => 3], 'label' => '学校', 'data' => 'id:name', 'conditionFields' => ['name']]<br>
				],<br>
				'radio-for-id' => [<br>
					//['field' => 'age', 'urlArgs' => ['tbFetcherId' => 3], 'label' => '优惠券/红包', 'data' => 'id:name,name', 'conditionFields' => ['name']]<br>
				],<br>
				'checkbox-for-id' => [<br>
					//['field' => 'age', 'urlArgs' => ['tbFetcherId' => 3], 'label' => '优惠券', 'data' => 'id:name,name', 'split' => ',', 'conditionFields' => ['name']]<br>
				],<br>
			];"],
			'field_table' => ['tips' => "\$public_button = [];<br>
				\$clos =[<br>
				'id' => ['sort' => true, 'float' => 'r'],<br>
				'name',<br>
				'age' => ['float' => 'r'],<br>
				'age2' => ['float' => 'r', 'type' => 'switch', 'val' => \$this->returnSelectByArr('switch', self::\$globalVar['selectByArr']['isEnable'])],<br>
				'age3' => ['float' => 'r', 'type' => 'switch', 'val' => \$this->returnSelectByModel(self::\$globalVar['selectByModel']['isEnableSwitch'])],<br>
				'age4' => ['type' => 'foreignKeyAuto', 'val' => 'ageName:name'],<br>
			];"],
			'field_edit' => ['tips' =>
				"\$edit_create = [<br>
					'notShow' => ['name', 'real_name'],<br>
					'show' => ['age'],<br>
					'hidden' => ['sid'],<br>
					'disable' => ['id'],<br>
					'default' => ['pwd' => ''],<br>
					'fieldType' => [<br>
						'descr'   => ['textarea', 100],<br>
						'isEnable' => \$this->returnSelectByArr('select', self::\$globalVar['selectByArr']['isEnable']),<br>
						'isEnable2' => \$this->returnSelectByModel(self::\$globalVar['selectByModel']['isEnable']),<br>
					],<br>
					'customStr' => false,<br>
				];<br>
				\$edit_modify = [<br>
					'notShow' => ['name', 'real_name'],<br>
					'show' => ['age'],<br>
					'hidden' => ['sid'],<br>
					'disable' => ['id'],<br>
					'default' => ['pwd' => ''],<br>
					'fieldType' => [<br>
						'descr'   => ['textarea', 100],<br>
						'isEnable' => \$this->returnSelectByArr('select', self::\$globalVar['selectByArr']['isEnable']),<br>
						'isEnable2' => \$this->returnSelectByModel(self::\$globalVar['selectByModel']['isEnable']),<br>
					],<br>
					'customStr' => false,<br>
				];<br>
				
				\$customHtml = [<br>
					'search-time-between' => [<br>
						//['field' => 'age', 'label' => 'AGE'],<br>
					],<br>
					'search-time' => ['age'],<br>
					'search-keyword-for-id' => [<br>
						//['field' => 'age', 'urlArgs' => ['tbFetcherId' => 3], 'label' => '学校', 'data' => 'id:name', 'conditionFields' => ['name']]<br>
					],<br>
					'radio-for-id' => [<br>
						//['field' => 'age', 'urlArgs' => ['tbFetcherId' => 3], 'label' => '优惠券/红包', 'data' => 'id:name,name', 'conditionFields' => ['name']]<br>
					],<br>
					'checkbox-for-id' => [<br>
						//['field' => 'age', 'urlArgs' => ['tbFetcherId' => 3], 'label' => '优惠券', 'data' => 'id:name,name', 'split' => ',', 'conditionFields' => ['name']]<br>
					],<br>
				];
			"],
		];
	}

	public function search($params)
	{
		$query = $this->find();
		$this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => ['id', 'task_id', 'parent_id',],
            '~' => ['title', 'tb', 'tb_create', 'field', 'field_attribute_label', 'field_rules', 'field_search', 'field_table', 'field_edit', 'field_data',],
        ]);
        return ['query' => $query];
	}

	public function getDbInfo()
	{
		return $this->hasOne(FetchTask::className(), ['id' => 'task_id']);
	}


	public function ListSearch()
	{
        return [
            'field' => ['id', 'task_id'],
            'key' => $this->modelName,
            'model' => $this,
        ];
	}

	public function ListTable()
	{
	    $sysParams = Yii::$app->sysParams;
		$tbIdKey = $sysParams->getParamsChild(['tableAutoId', 'fetcher']);
		$holdCommonArgs = $sysParams->getParamsChild(['holdArgs', 'common']);
		$configKey = $sysParams->getParamsChild(['tableAutoConfig', 'configTable', 'tbId']);

        return [
            'publicButton' => ['create' => ['onclick' => AdminListConfig::returnCreateUrl(), 'title' => '添加']],
            'field' => [
                'id' => ['sort' => true, 'float' => 'r'],
                'task_id' => ['sort' => true, 'type' => 'foreignKey', 'val' => 'fetchTask:title'],
                'title',
                'parent_id' => ['float' => 'r'],
                'tb',
            ],
            'recordOperation' => [
                ['title' => '数据', 'url' => "/fetch-auto-model/index?{$tbIdKey}=%s&{$holdCommonArgs}={$tbIdKey}", 'type' => 'box', 'authority' => 'fetch-task-item/index'],
                'config-table' => [
                    'title' => '配置表',
                    'url' => "/fetch-task/config-table?{$configKey}=%s",
                    'type' => 'box',
                    'authority' => 'fetch-task/config-table'
                ],
                'view', 'update', 'delete'
            ],
            'model' => $this,
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
                'id' => ['showType' => 'disable'],
                'tb_create' => ['type' => 'textarea', 'length' => 0, 'height' => '150px'],
                'field' => ['type' => 'textarea', 'length' => 0, 'height' => '150px'],
                'field_global_var' => ['type' => 'textarea', 'length' => 0, 'height' => '150px'],
                'field_attribute_label' => ['type' => 'textarea', 'length' => 0, 'height' => '150px'],
                'field_attribute_labels_config' => ['type' => 'textarea', 'length' => 0, 'height' => '150px'],
                'field_rules' => ['type' => 'textarea', 'length' => 0, 'height' => '150px'],
                'field_search' => ['type' => 'textarea', 'length' => 0, 'height' => '150px'],
                'field_search_box' => ['type' => 'textarea', 'length' => 0, 'height' => '150px'],
                'field_table' => ['type' => 'textarea', 'length' => 0, 'height' => '150px'],
                'field_edit' => ['type' => 'textarea', 'length' => 0, 'height' => '150px'],
                'field_data' => ['type' => 'textarea', 'length' => 0, 'height' => '150px'],
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

	public function getFetchTask()
	{
		return $this->hasOne(FetchTask::className(), ['id' => 'task_id']);
	}
}
