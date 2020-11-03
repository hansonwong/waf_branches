<?php
namespace app\models;

use Yii;

class SysUserForSelf extends SysUserForRole
{
    public function rulesSource()
    {
        $rules = parent::rulesSource();
        $rules[] = [['pwd', 'pwd_confirm', 'pwd_old'], 'required'];
        $rules[] = [['pwd_old'], function($attribute, $params){
            $user = Yii::$app->sysLogin->getUser();
            if(!$user->validatePasswordForNoAuthcode($this->$attribute)){
                $tips = Yii::$app->sysLanguage->getTranslateBySymbol('oldPwdError');
                $this->addError($attribute, $tips);
            }
        }];
        return $rules;
    }

    public function afterSave($insert, $changedAttributes)
    {
        parent::afterSave($insert, $changedAttributes);
        $user = Yii::$app->sysLogin->getUser();
        $sysLoginConfig = new \app\logic\sys\SysLoginConfig();
        $sysLoginConfig->updateUserLoginCount($user, true);
    }

    public function ListField()
	{
		$fieldKey = $this->modelName;

		$fieldType = [
		    'id' => ['showType' => 'hidden'],
		    'group_id' => ['showType' => 'notShow'],
		    'name' => ['showType' => 'notShow'],
		    'enable' => ['showType' => 'notShow'],
            'pwd' => ['type' => 'password', 'default' => ''],
            'pwd_confirm' => ['type' => 'password'],
            'pwd_old' => ['type' => 'password'],
        ];
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => $fieldType,
            'customStr' => false,
        ];
		return $field;
	}
}
