<?php
namespace app\logic\sys;

use Yii;

class LogCommon
{
    /**
     * 写入操作日志
     * @param $content
     * @param $success
     */
	public static function insertFirewallOperationLog($content, $success){
        if(!Yii::$app->sysParams->getFirewallSystemStatus()) return;
	    Yii::$app->sysLanguage->setLanguageBySystemDefault();#设置系统默认语言

	    $user = Yii::$app->sysLogin->getUser();
	    $model = new \app\modelFirewallLogs\Operatelog();
        $model->iDateTime = time();
        $model->sIp = Yii::$app->request->userIP;
        $model->sOperateUser = $user->name ?? '?';
        $model->sRs = $success ?
            Yii::$app->sysLanguage->getTranslateBySymbol('operationSuccess'):
            Yii::$app->sysLanguage->getTranslateBySymbol('operationFailed');
        $model->sContent = $content;
        $model->sOperateAction = "waf: ".Yii::$app->controller->module->requestedRoute;
        $model->save(false);

        Yii::$app->sysLanguage->initLanguage();#设置当前默认语言
    }

    /**
     * 写入登录日志
     * @param $user
     * @param $userNameInput
     * @param $content
     * @param $success
     */
    public static function insertFirewallLoginLog($user, $userNameInput, $content, $success){
        if(!Yii::$app->sysParams->getFirewallSystemStatus()) return;
        Yii::$app->sysLanguage->setLanguageBySystemDefault();#设置系统默认语言

        $model = new \app\modelFirewallLogs\LoginLog();

        $model->iUserId = $user->name ?? \yii\helpers\HtmlPurifier::process($userNameInput);
        $model->iLoginTime = time();
        $model->sIp = Yii::$app->request->userIP;
        $model->sStatus = 1;
        $model->sContent = $success ?
            Yii::$app->sysLanguage->getTranslateBySymbolWithSourceLanguage('loginSuccess'):
            $content;

        $model->save(false);

        Yii::$app->sysLanguage->initLanguage();#设置当前默认语言
    }

    /**
     * 为控制器写入操作日志
     * @param $controller
     */
    public static function insertFirewallOperationLogForBaseController($controller){
        if(!Yii::$app->sysParams->getFirewallSystemStatus()) return;
        $route = Yii::$app->requestedRoute;
        $action = end(explode('/', $route));
        $menuSelf = \app\models\SysUserMenu::findOne(['url' => $route]);
        $menuParent = $menuSelf ? \app\models\SysUserMenu::findOne(['id' => $menuSelf->parent_id]) : null;

        $isGet = Yii::$app->request->isGet;
        $isPost = Yii::$app->request->isPost;

        $actionStr = '';
        if($menuSelf){
            switch($action){
                case 'index':
                    $actionStr = 'see';
                    break;
                case 'config':
                    $actionStr = $isGet ? 'see' : 'config';
                    break;
                case 'create':
                    $actionStr = $isGet ? '' : 'create';
                    break;
                case 'update':
                    $actionStr = $isGet ? 'see' : 'update';
                    break;
                case 'delete':
                    $actionStr = 'delete';
                    break;
                case 'export':
                    $actionStr = 'export';
                    break;
                case 'import':
                    $actionStr = 'import';
                    break;
                default:
                    $actionStr = $isGet ? 'see' : 'config';
            }

            if($actionStr && $controller->actionResultLog){
                $actionStr = Yii::$app->sysLanguage->getTranslateBySymbol($actionStr);

                $translateKey = $menuParent ? "%s >> %s : %s" : "%s : %s";
                $translateData = $menuParent ?
                    [$menuParent->name, $menuSelf->name, $actionStr] : [$menuSelf->name, $actionStr];
                $content = Yii::$app->sysLanguage->JsonVsprintfSet($translateKey, $translateData);
                self::insertFirewallOperationLog($content, $controller->actionResult);
            }
        }
    }
}