<?php
namespace app\models;

use Yii;
use \yii\helpers\Url;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;

class SysUserGroup extends \app\logic\model\BaseModel
{
	public static function tableName()
	{
		return 'sys_user_group';
	}

	public function rulesSource()
	{
		return [
			[['id', 'enable'], 'integer'],
			[['group_name'], 'string', 'max' => 100],
            [['firewall_user_role'], 'string', 'max' => 20],
			[['descr'], 'string', 'max' => 300],
			[['group_name'], 'unique'],
		];
	}

	public function attributeLabelsSource()
	{
		return [
			'id' => 'ID',
			'group_name' => '组别',
            'firewall_user_role' => '防火墙角色',
			'enable' => '可用',
			'descr' => '描述',
		];
	}

	public function afterDelete()
    {
        parent::afterDelete();
        \app\logic\sys\SysAuthority::deleteAuthorityCache($this->id);//删除单一缓存
    }

    public function search($params)
	{
		$query = $this->find();
		$this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => ['id', 'enable',],
            '~' => ['group_name', 'descr',],
        ]);
        return ['query' => $query];
	}

	public function ListSearch()
	{
        return [
            'field' => ['id', 'group_name', 'enable' => SelectList::enable('select'),],
            'key' => $this->modelName,
            'model' => $this,
        ];
	}

	public function ListTable()
	{
	    return [
	        'publicButton' => [],
            'field' => [
	            'id' => ['sort' => true, 'float' => 'r'], 'group_name',
                'enable' => ['float' => 'c', 'type' => 'switch', 'val' => SelectList::enable('switch')],
                'descr'
            ],
            'recordOperation' => [
                ['title' => '权限', 'url' => str_replace('%2F', '/', Url::to(['authority'])).'&id=%s', 'type' => 'box', 'authority' => 'sys-user-group/authority'],
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
                'enable' => SelectList::enable('select'),
                'firewall_user_role' => SelectList::systemFirewallUserRole('select'),
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
