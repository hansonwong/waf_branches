<?php
namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;;
use app\logic\SysParams;

class FetchTask extends BaseModel
{
	public static function tableName()
	{
		return 'fetch_task';
	}

	public function rulesSource()
	{
		return [
			[['id'], 'integer'],
			[['title'], 'string', 'max' => 100],
			[['host', 'db', 'user', 'pwd'], 'string', 'max' => 30],
		];
	}

	public function attributeLabelsSource()
	{
		return [
			'id' => 'ID',
			'title' => 'Title',
			'host' => 'Host',
			'db' => 'Db',
			'user' => 'User',
			'pwd' => 'Pwd',
		];
	}

	public function afterSave($insert, $changedAttributes){
		parent::afterSave($insert, $changedAttributes);
		if($insert){
			$db = new \yii\db\Connection([
				'dsn' => "mysql:host={$this->host};",
				'username' => $this->user,
				'password' => $this->pwd,
				'charset' => 'utf8',
			]);
			$db->createCommand("create database {$this->db}")->query();
		}
	}

	public function search($params)
	{
		$this->load($params);
		$query = $this->find();
        $this->searchFilterHelper($query, $this, [
            '=' => ['id',],
            '~' => ['title', 'db', 'host'],
        ]);
        return ['query' => $query];
	}

	public function getTables(){
		return $this->hasMany(FetchTaskItem::className(), ['task_id' => 'id']);
	}

	public function ListSearch()
	{
        return [
            'field' => ['id', 'title', 'host', 'db'],
            'key' => $this->modelName,
            'model' => $this,
        ];
	}

	public function ListTable()
	{
		$holdModelArgs = SysParams::getParamsChild(['holdArgs', 'model']);
		$configKey = SysParams::getParamsChild(['tableAutoConfig', 'configTable', 'dbId']);

        return [
            'field' => ['id' => ['sort' => true, 'float' => 'r'], 'title', 'host', 'db'],
            'recordOperation' => [
                'install-base' => [
                    'title' => '安装库',
                    'url' => 'install-base?id=%s',
                    'type' => 'box',
                ],
                'config-table' => [
                    'title' => '配置表',
                    'url' => "config-table?{$configKey}=%s",
                    'type' => 'box',
                ],
                [
                    'title' => '表项',
                    'url' => "/fetch-task-item/index?FetchTaskItem[task_id]=%s&{$holdModelArgs}=task_id",
                    'type' => 'box',
                    'authority' => 'fetch-task-item/index'
                ],
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
            'fieldType' => [],
            'customStr' => false,
        ];
		switch ($type) {
			case 'create' :
				break;
			case 'update' :
				break;
			default :;
		}
		return $field;
	}
}
