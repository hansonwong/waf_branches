<?php
namespace app\models;

use Yii;

class SysUserMenu extends \app\logic\model\BaseModel
{
    public $enable;

    public static function tableName(){
        return 'sys_user_menu';
    }

    public function rulesSource()
    {
        return [
            [['id', 'parent_id', 'enable', 'display_child', 'sort'], 'integer'],
            [['url', 'descr'], 'string', 'max' => 300],
            [['name', 'icon_class'], 'string', 'max' => 30],
        ];
    }

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => ['id', 'parent_id', 'sort',],
            '~' => ['url', 'descr', 'name'],
        ]);
        return ['query' => $query];
    }
    
    public function attributeLabelsSource()
    {
        return [
            'id' => '',
            'name' => '',
            'parent_id' => '',
            'url' => '',
            'sort' => '',
            'descr' => '',
            'icon_class' => '',
        ];
    }

    public function afterSave($insert, $changedAttributes){
        parent::afterSave($insert, $changedAttributes);
        \app\logic\sys\SysMenu::saveSingle($this);
        \app\logic\sys\SysAuthority::deleteAuthorityCache(false);//删除所有缓存
    }

    public function afterDelete()
    {
        \app\logic\sys\SysAuthority::deleteAuthorityCache(false);//删除所有缓存
    }

    public function getEnable()
    {
        return $this->hasOne(SysUserMenuEnable::className(), ['id' => 'id']);
    }
}
