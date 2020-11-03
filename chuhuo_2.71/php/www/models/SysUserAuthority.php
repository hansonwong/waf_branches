<?php
namespace app\models;

class SysUserAuthority extends \app\logic\model\BaseModel
{
    public static function tableName()
    {
        return 'sys_user_authority';
    }

    public function rulesSource()
    {
        return [
            [['id', 'group_id', 'sys_menu_id', 'enable'], 'integer'],
        ];
    }

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => ['id', 'group_id', 'sys_menu_id', 'enable'],
        ]);
        return ['query' => $query];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'group_id' => 'Group ID',
            'sys_menu_id' => 'Sys Menu ID',
            'enable' => 'Enable',
        ];
    }

    public function getSysUserMenu(){
        return $this->hasOne(SysUserMenu::className(), ['id' => 'sys_menu_id']);
    }
}
