<?php
namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;

class SysLoginConfig extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function attributeLabelsSource()
    {
        return [
            'maxError' => 'loginErrorLimit',
            'lockTime' => 'loginErrorLockTime',
            'maxTimeout' => 'loginTimeoutTime',
            'singleUserLoginCountLimit' => 'singleUserLoginCountLimit',
            'systemDefaultLanguage' => 'systemDefaultLanguage',
        ];
    }

    public function rulesSource()
	{
		return [
		    //maxError 最大错误次数
            //lockTime 错误后锁定账号N分钟
            //maxTimeout 登录最长时间
            [['singleUserLoginCountLimit'], 'required'],
            [['maxError', 'lockTime', 'maxTimeout', 'singleUserLoginCountLimit'], 'integer', 'min' => 1],
            [['maxTimeout'], 'integer', 'max' => 1440],
            [['systemDefaultLanguage'], 'string'],
		];
	}

    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'systemDefaultLanguage' => SelectList::systemDefaultLanguage('select'),
            ],
            'customStr' => false,
        ];
        return $field;
    }

    public function save(){
        $result = parent::save();
        $this->saveForFirewall();
        Yii::$app->sysLogin->isLogin();//刷新登录超时时间
        return $result;
    }

    public function saveForFirewall(){
        $model = \app\modelFirewall\Config::findOne(['sName' => 'WebSet']);
        $json = json_decode($model->sValue);
        $json->iTimeOut = $this->maxTimeout;
        $json->iLoginLimit = $this->singleUserLoginCountLimit;
        $model->sValue = json_encode($json);
        $model->save(false);
    }
}
