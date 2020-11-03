<?php
namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;

class SysUserForRole extends SysUser
{
	public function search($params)
	{
	    $user = Yii::$app->sysLogin->getUser();
		$query = $this->find();
		$this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => ['enable', ['group_id' => $user->group_id],],
            '~' => ['name',],
        ]);
        return ['query' => $query];
	}

	public function beforeSave($insert)
	{
        $user = Yii::$app->sysLogin->getUser();
        $this->group_id = $user->group_id;
		if (parent::beforeSave($insert)) {

			return true;
		} else {
			return false;
		}
	}

    public function beforeDelete()
    {
        $user = Yii::$app->sysLogin->getUser();
        if($this->group_id != $user->group_id) return false;
        return parent::beforeDelete();
    }

	public function ListSearch()
	{
        return [
            'field' => ['name',
                'enable' => SelectList::enable('select'),
            ],
            'key' => $this->modelName,
            'model' => $this,
        ];
	}

	public function ListField()
	{
		$type = AdminListConfig::ListFieldScenarios('common', $this);
		$fieldKey = $this->modelName;

		$fieldType = [
		    'id' => ['showType' => 'hidden'],
		    'group_id' => ['showType' => 'notShow'],
            'pwd_old' => ['showType' => 'hidden'],
            'pwd' => ['type' => 'password', 'default' => ''],
            'pwd_confirm' => ['type' => 'password'],
            'enable' => SelectList::enable('select'),
        ];
		switch ($type) {
			case 'create' :
				break;
			case 'update' :
                $fieldType['name']['showType'] = 'show';
				break;
			default :
				;
		}
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => $fieldType,
            'customStr' => false,
        ];
		return $field;
	}
}
