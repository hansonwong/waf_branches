<?php
namespace app\controllers;

use Yii;

class SysUserConfigController extends \app\logic\BaseController
{
	public function actionModifyInfo()
	{
		if (Yii::$app->request->isPost) {
			$post = Yii::$app->request->post();
			$pwd1 = $post['pwdN'][0];
			$pwd2 = $post['pwdN'][1];

			$error = false;
			if ($pwd1 != $pwd2) {
				$error = $this->translate->getTranslateBySymbol('confirmPasswordInconsistency');
			} else if ('' == $pwd1) {
				$error = $this->translate->getTranslateBySymbol('newPasswordCanNotEmpty');
			}
            if($error) Yii::$app->sysJsonMsg->msg(false, $error);

            $sysLogin = Yii::$app->sysLogin;
			$user = $sysLogin->getUser();

			$user->setAttribute('pwd', $pwd1);
			$user->save(false);
            #统计操作信息,不再使用
			#LogCommon::logCreate('admin', 'modifyPersonInfo', '', "{$user->id}/{$user->name}:修改个人信息", '', $user->id, '');
            Yii::$app->sysJsonMsg->msg(true, '');
		} else {
			return $this->renderPartial('modify-info', []);
		}
	}
}
