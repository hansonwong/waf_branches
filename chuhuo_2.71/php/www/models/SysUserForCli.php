<?php
namespace app\models;

use Yii;

class SysUserForCli extends SysUser
{
    public function pwdSave($pwd){
        $this->pwd = self::pwdMake($pwd);
        return $this->save(false);
    }

	public function beforeSave($insert)
	{
		return true;
	}
}
