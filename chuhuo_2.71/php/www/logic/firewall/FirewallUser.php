<?php
namespace app\logic\firewall;

use Yii;
use app\modelFirewall\Account;

class FirewallUser
{
    /**
     * 防火墙密码加密
     * @param    string      $string 加密内容
     * @param    string      $operation 加密动作
     * @param    string      $key 私钥
     * @param    int         $expiry 有效时间秒
     * @return   string      加密串
     */
    public static function authcode($string, $operation = 'DECODE', $key = '', $expiry = 0)
    {
        $ckey_length = 4;
        $key = md5($key);
        $keya = md5(substr($key, 0, 16));
        $keyb = md5(substr($key, 16, 16));
        $keyc = $ckey_length ? ($operation == 'DECODE' ? substr($string, 0, $ckey_length): substr(md5(microtime()), -$ckey_length)) : '';
        $cryptkey = $keya.md5($keya.$keyc);
        $key_length = strlen($cryptkey);
        $string = $operation == 'DECODE' ? base64_decode(substr($string, $ckey_length)) : sprintf('%010d', $expiry ? $expiry + time() : 0).substr(md5($string.$keyb), 0, 16).$string;
        $string_length = strlen($string);
        $result = '';
        $box = range(0, 255);
        $rndkey = array();
        for($i = 0; $i <= 255; $i++)
        {
            $rndkey[$i] = ord($cryptkey[$i % $key_length]);
        }
        for($j = $i = 0; $i < 256; $i++)
        {
            $j = ($j + $box[$i] + $rndkey[$i]) % 256;
            $tmp = $box[$i];
            $box[$i] = $box[$j];
            $box[$j] = $tmp;
        }
        for($a = $j = $i = 0; $i < $string_length; $i++)
        {
            $a = ($a + 1) % 256;
            $j = ($j + $box[$a]) % 256;
            $tmp = $box[$a];
            $box[$a] = $box[$j];
            $box[$j] = $tmp;
            $result .= chr(ord($string[$i]) ^ ($box[($box[$a] + $box[$j]) % 256]));
        }
        if($operation == 'DECODE')
        {
            if((substr($result, 0, 10) == 0 || substr($result, 0, 10) - time() > 0) && substr($result, 10, 16) == substr(md5(substr($result, 26).$keyb), 0, 16))
            {
                return substr($result, 26);
            }else{
                return '';
            }
        }else{
            return $keyc.str_replace('=', '', base64_encode($result));
        }
    }

    /**
     * waf单账号同步到防火墙
     * @param $user
     */
    public static function userCreateModify($user){
        if(!Yii::$app->sysParams->getFirewallSystemStatus()) return;
        $model = Account::findOne($user->id);
        if(null === $model) $model = new Account();
        $model->iUserId = $user->id;
        $model->sLoginAccount = $model->sUerName = $user->name;
        $model->sPasswd = self::getFirewallPwd($user);
        $model->sRole = $user->sysUserGroup->firewall_user_role;
        $model->iStatus = 4;
        $model->save(false);
    }

    /**
     * 获取防火墙用户密码或加密后的密码
     * @param $user
     * @param bool $encrypt
     * @return string
     */
    protected static function getFirewallPwd($user, $encrypt = true){
        $pwd = "{$user->name}:{$user->id}:{$user->pwd}";
        return $encrypt ? md5($user->id . md5($pwd)) : $pwd;
    }

    /**
     * 返回防火墙用户登录验证的信息
     * @param $user
     * @return array
     */
    public static function getFirewallLoginVerify($user){
        if(!Yii::$app->sysParams->getFirewallSystemStatus()) return [];
        return ['verify' => [
            'sAccountName' => $user->name,
            'sPassWord' => self::authcode(self::getFirewallPwd($user,false), 'ENCODE', $user->name, 5),
        ]];
    }

    /**
     * 删除防火墙用户
     * @param $user
     */
    public static function deleteFirewallUser($user){
        $firewallUser = Account::findOne($user->id);
        $firewallUser->delete();
    }

    /**
     * waf账号一次性同步到防火墙账号中
     * @param bool $limit 是否限制使用
     */
    public static function syncWafAndFirewallUser($limit = false){
        if($limit){
            if (!YII_ENV_DEV) return;
        }
        Account::deleteAll();
        $wafUsers = \app\models\SysUser::find()->all();
        foreach ($wafUsers as $wafUser) self::userCreateModify($wafUser);
    }

    /**
     * 更新用户密码
     * @param $userName
     * @param $pwd
     * @return bool|void
     */
    public static function updateUserPwd($userName, $pwd){
        $user = \app\models\SysUserForCli::findOne(['name' => $userName]);
        return (!$user) ? false : $user->pwdSave($pwd);
    }
}