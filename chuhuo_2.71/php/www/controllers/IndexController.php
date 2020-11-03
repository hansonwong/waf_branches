<?php

namespace app\controllers;

use Yii;
use app\logic\sys\SysAuthority;

class IndexController extends \app\logic\BaseController
{
    //public $enableCsrfValidation = false;

    public function beforeAction($action)
    {
        $needCsrf = ['login-check'];

        if (!in_array($action->id, $needCsrf)) {
            $action->controller->enableCsrfValidation = false;
        }
        return parent::beforeAction($action);
    }


    public function actions()
    {
        return [
            'captcha' => [
                'class' => 'yii\captcha\CaptchaAction',
                'fixedVerifyCode' => YII_ENV_DEV ? '' : null,
                'backColor' => 0x000000,//背景颜色
                'maxLength' => 4, //最大显示个数
                'minLength' => 4,//最少显示个数
                'padding' => 5,//间距
                'height' => 40,//高度
                'width' => 130,  //宽度
                'foreColor' => 0xffffff,     //字体颜色
                'offset' => 4,        //设置字符偏移量 有效果
                //'controller'=>'login',        //拥有这个动作的controller
            ],
        ];
    }

    //首页
    public function actionIndex()
    {
        $sysLogin = Yii::$app->sysLogin;
        if (!$sysLogin->isLogin()) return $this->renderPartial('login', [
            'enableFirewall' => Yii::$app->sysParams->getFirewallSystemStatus(),
        ]);
        $user = $sysLogin->getUser();
        return $this->renderPartial('index', [
            'isNeedResetPwd' => $sysLogin->isNeedResetPwd(),
            'adminInfo' => $user,
            'menu' => SysAuthority::getMenu($user->group_id),
        ]);
    }

    //登录检测
    public function actionLoginCheck()
    {
        Yii::$app->sysLogin->Login(Yii::$app->request->post());
    }

    //退出登录
    public function actionLogout()
    {
        Yii::$app->sysLogin->Logout();
    }

    /**
     * 同步waf账号到防火墙系统中
     */
    public function actionSyncWafAndFirewallUser()
    {
        \app\logic\firewall\FirewallUser::syncWafAndFirewallUser(true);
    }
}
