<?php

namespace app\models;

use Yii;

class SysUserMenuEnable extends \yii\db\ActiveRecord
{
    public static function tableName()
    {
        return 'sys_user_menu_enable';
    }

    public function rules()
    {
        return [
            [['id'], 'required'],
            [['id', 'enable'], 'integer'],
            [['id'], 'exist', 'skipOnError' => true, 'targetClass' => SysUserMenu::className(), 'targetAttribute' => ['id' => 'id']],
        ];
    }

    public function attributeLabels()
    {
        return [
            'id' => 'ID',
            'enable' => 'Enable',
        ];
    }

    public function getSysUserMenu()
    {
        return $this->hasOne(SysUserMenu::className(), ['id' => 'id']);
    }
}