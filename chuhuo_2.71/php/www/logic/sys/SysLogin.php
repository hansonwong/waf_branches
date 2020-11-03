<?php
namespace app\logic\sys;

use Yii;
use yii\captcha\CaptchaValidator;
use app\models\SysUser;

class SysLogin
{
    //获取登录用户对象
	public static function getUser()
	{
		return Yii::$app->admin->identity;
	}

    //判断是否超级管理员
	public static function isSuperAdmin(){
        $user = self::getUser();
        return (1 == $user->group_id);
    }

	//判断用户是否登录
	public static function isLogin()
	{
	    //检查是否超出登录有效时间
        $sysLoginConfig = new SysLoginConfig();
	    if($sysLoginConfig->checkTimeOut()) return false;

		$admin = Yii::$app->admin;
		return ($admin->isGuest) ? false : true;
	}

	public static function isNeedResetPwd(){
        $model = new \app\models\PasswordPolicy();
        $user = self::getUser();
        $sym = false;
        if(1 == $model->modifyPwdFirst){
            if(in_array($user->login_time, [0])) $sym = true;
        }
        if(0 < $model->expirationTime){
            $time = (int) time();
            $expirationTime = $user->pwd_up_time + ($model->expirationTime * 60 * 60 * 24);
            if($time > $expirationTime) $sym = true;
        }

        return $sym;
    }

	public static function validatorCaptcha($value)
	{
		$caprcha = new CaptchaValidator();
		$caprcha->captchaAction = 'index/captcha';
		return $caprcha->validate($value);
	}

	public static function Login($data)
	{
	    $loginConfig = new SysLoginConfig();
		$user = SysUser::findByUsername($data['name']);

        $msg = '';
		if (!self::validatorCaptcha($data['cap'])) {//验证码
            $msg = Yii::$app->sysLanguage->getTranslateBySymbol('verificationCodeError');
            $logMsg = Yii::$app->sysLanguage->getTranslateBySymbolWithSourceLanguage('verificationCodeError');
		} elseif(!$user) {//账号错误
            $msg = Yii::$app->sysLanguage->getTranslateBySymbol('invalidUser');
            $logMsg = Yii::$app->sysLanguage->getTranslateBySymbolWithSourceLanguage('invalidUser');
		} elseif(!$loginConfig->isAllowSuperAdmin($user)){//是否允许超级管理员
            $msg = Yii::$app->sysLanguage->getTranslateBySymbol('invalidUser');
            $logMsg = Yii::$app->sysLanguage->getTranslateBySymbolWithSourceLanguage('invalidUser');
        }elseif(!$loginConfig->isPass($user)){//是否允许登录
            $msg = $loginConfig->errorInfo;
        } elseif (!$user->validatePassword($data['pwd'])) {//密码验证
            $tryCount = $loginConfig->loginError($user);
            $msg = Yii::$app->sysLanguage->getTranslateBySymbol('userNameAndPwdError');
			$msg = sprintf($msg, $tryCount);
            $logMsg = Yii::$app->sysLanguage->getTranslateBySymbolWithSourceLanguage('passwordError');
		} elseif ('1' != $user->sysUserGroup->enable) {//所属组别是否可登录
            $msg = Yii::$app->sysLanguage->getTranslateBySymbol('userLoginBlock');
            $logMsg = Yii::$app->sysLanguage->getTranslateBySymbolWithSourceLanguage('userLoginBlock');
		} else {//登录成功
			$result = Yii::$app->admin->login($user, 0);
			if ($result) {#登录成功
                $loginConfig->loginSuccess($user);
                Yii::$app->sysJsonMsg->data(true, \app\logic\firewall\FirewallUser::getFirewallLoginVerify($user));
			} else {
                $msg = Yii::$app->sysLanguage->getTranslateBySymbol('loginFailed');
                $logMsg = Yii::$app->sysLanguage->getTranslateBySymbolWithSourceLanguage('loginFailed');
			}
		}
        Yii::$app->logCommon->insertFirewallLoginLog($user, $data['name'], $logMsg, false);#记录错误登录日志
        Yii::$app->sysJsonMsg->msg(false, $msg);
	}

	public static function Logout()
	{
		$admin = Yii::$app->admin;
		$user = $admin->identity;
		$admin->logout();
	}
}