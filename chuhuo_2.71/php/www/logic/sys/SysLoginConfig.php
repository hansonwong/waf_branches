<?php
namespace app\logic\sys;

use Yii;
use app\models\SysUser;
use app\modelFirewall\Timeout;

class SysLoginConfig{
    protected $modelUser = null;//用户model
    public $errorInfo = null,//登录错误提示
        $model = null;//验证model

    public function __construct()
    {
        $this->model = new \app\models\SysLoginConfig();
    }

    /**
     * 是否允许超级管理员登录,在开发模式下允许
     * @param $user
     */
    public function isAllowSuperAdmin($user){
        if(1 == $user->group_id)
            if(!YII_ENV_DEV) return false;
        return true;
    }

    public function defaultLanguage(){
        $config = $this->model->get(false);
        return $config->systemDefaultLanguage ?? Yii::$app->sysLanguage->defaultLanguage;
    }

    /**
     * 重置用户错误信息
     * @param $user
     */
    public function resetUserError($user){
        $user->offsetUnset('pwd');
        $user->error_count = 0;
        $user->error_lock_time = 0;
        $user->save(false);
    }

    /**
     * 更新用户登录次数
     * @param $user
     * @param $force 是否强制
     */
    public function updateUserLoginCount($user, $force = false){
        $user->offsetUnset('pwd');
        $model = new \app\models\PasswordPolicy();
        if(false == $force && 1 == $model->modifyPwdFirst){
            if(in_array($user->login_time, [0])) return;
        }
        $user->login_time = $user->login_time + 1;
        $user->save(false);
    }

    /**
     * 判断用户是否可以继续登录
     * @param $user
     */
    public function isPass($user){
        $config = $this->model->get(false);
        $sym = true;
        if($user->error_count >= $config->maxError){
            $timeLimit = $config->lockTime * 60;
            $timeOver = intval(time()) - $user->error_lock_time;
            $timeLeft = $timeLimit - $timeOver;
            $sym = !($timeLimit >= $timeOver);
            if(0 >= $timeLeft) $this->resetUserError($user);
            $info = Yii::$app->sysLanguage->getTranslateBySymbol('loginErrorLockTips');
            $this->errorInfo = sprintf($info, $user->error_count, $timeLeft);
        }
        return $sym;
    }

    /**
     * 检查超出登录有效时间
     * @param $user
     */
    public function checkTimeOut(){
        if(intval(time()) > $this->loginExpireTime()) return true;
        if($this->checkTimeOutForRoute()) $this->loginExpireTime('set');
        return false;
    }

    /**
     * 判断路由是否更新登录超时时间
     */
    protected function checkTimeOutForRoute(){
        $routePassForLoginTimeout = Yii::$app->sysPath->routePassForLoginTimeout;
        $route = Yii::$app->controller->module->requestedRoute;
        $controller = Yii::$app->controller->id;

        if(in_array($route, $routePassForLoginTimeout['routeException'])) return true;
        if(in_array($route, $routePassForLoginTimeout['route'])) return false;
        if(in_array($controller, $routePassForLoginTimeout['controller'])) return false;
        return true;
    }

    /**
     * 登录失败记录失败次数加1,返回剩余次数
     * @param $user
     */
    public function loginError($user){
        $config = $this->model->get(false);
        $user->offsetUnset('pwd');
        $user->error_count += 1;
        $user->error_lock_time = time();
        $user->save(false);
        return ($user->error_count <= $config->maxError) ?
            $config->maxError - $user->error_count : 0;
    }

    /**
     * 登录成功清空记录失败
     * @param $user
     */
    public function loginSuccess($user){
        if(!Yii::$app->sysParams->getFirewallSystemStatus()){
            $config = $this->model->get(false);
            $timeLimit = $config->maxTimeout * 60;

            $model = new Timeout();
            $model->iSessionId = self::getSessionId();
            $model->expireTime = $model->iSessionTimeout = intval(time()) + $timeLimit;
            $model->save(false);
        }
        $this->resetUserError($user);
        $this->updateUserLoginCount($user);
    }

    /**
     * 获取/更新登录超时时间
     * @param string $type
     */
    public function loginExpireTime($type = 'get'){
        $model = Timeout::findOne(['iSessionId' => self::getSessionId()]);
        if(null === $model) return 0;
        switch($type){
            case 'get' :
                return intval($model->expireTime);
                break;
            case 'set' :
                $config = $this->model->get(false);
                $timeLimit = $config->maxTimeout * 60;
                $model->expireTime = $model->iSessionTimeout = intval(time()) + $timeLimit;
                $model->save(false);
                break;
        }
    }

    /**
     * 获取session key
     * @return mixed
     */
    public static function getSessionId(){
        return $_COOKIE[Yii::$app->sysInfo->systemSessionKey] ?? Yii::$app->session->id;#$_COOKIE[Yii::$app->session->name];
    }
}