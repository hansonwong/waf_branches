<?php
namespace app\controllers;

use Yii;

class SysUserForRoleController extends \app\logic\BaseController{
    public function actionChangeSelfPwd(){
        $this->model = "{$this->modelPrimaryNameSpace}SysUserForSelf";
        $user = Yii::$app->sysLogin->getUser();
        return parent::actionUpdate($user->id);
    }
}
