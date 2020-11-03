<?php

/**
 * User: mallor <mallor@163.com>
 * Date: 13-6-19
 * Time: 下午3:48
 * @since 1.0
 * @id: SiteController.php
 * 描述：后台首页管理入口
 * 修改时间：
 * 修改功能描述：
 */
class SiteController extends MqController
{
    //验证码超时时间
    private $limit_time = 3;

    public $enableCSRF=true;//是否开启csrf验证
    //执行action前的处理
    public function beforeAction($action)
    {
        //对当前控制器启用CSRF认证
        //$this->validateCsrfToken();
		$url = Yii::app()->request->url;
		if(strtolower($url) == strtolower('Site/LoginSystemWaf')){
			yii::app()->request->enableCsrfValidation = false;
		}
        return parent::beforeAction($action);
    }
    //验证csrf
    protected function validateCsrfToken()
    {
        if ($this->enableCSRF == true) {
            yii::app()->request->enableCsrfValidation = true;//属性改为true，以便CHtml::beginForm()生成csrf_token
            yii::app()->request->validateCsrfToken('');
        }
    }
    public function accessRules()
    {
        return array(
            array('allow',
                'actions' => array('captcha','System', 'Index', 'UserLogin', 'GetDataMsg', 'LoginSystem', 'LoginSystemWaf', 'InstallEPass', 'TouchFile', 'OutLine', 'Error', 'NoIn', 'UsersAuthDown', 'Import_tpl', 'SendMsgJXXT', 'SendMsgBXT','CheckUsbkey'),
                'users' => array('*'),
            ),
            array('allow',
                'actions' => array('LogoutSys', 'UsersAuthDown', 'Import_tpl'),
                'users' => array('@'),
            ),
            array('deny',
                'deniedCallback' => function () {
                    $this->redirect(array('NoIn'));
                },
                'users' => array('*'),
            ),
        );

    }

    public function actions()
    {
        return array(
            'captcha' => array(
                'class' => 'CCaptchaAction',
                'testLimit' => 1, ///如果要每次都变的话，还需要设置这里面的 testLimit 为 1
                'padding' => 2, //文字周边填充大小
                'backColor' => 0xcce9f6,
                'maxLength' => 4,       // 最多生成几个字符
                'minLength' => 4,       // 最少生成几个字符
            ),
        );
    }

    /**
     * IP受权
     */
    public function actionNo()
    {
        $this->comeIn();
    }

    /**
     * 非无权限访问 YII
     */
    public function actionNoIn()
    {
        $this->render('no_in');
    }

    public function actionCaptchaCode()
    {
        $image_model = new ImageCaptcha();
        //可以在此处更改属性达到验证码不同大小的图片
        $image_model->outputBrowser();
        Yii::app()->end();
    }

    /**
     * 首页
     */
    public function actionIndex()
    {
        $sym = false;
        if(isset($_GET['waf'])){
            if('firewall' == $_GET['waf']) $sym = true;
        }
        if(!$sym){
            header('Location: /');
            return;
        }
        if (Yii::app()->user->getId()) {
            $aUserRoleData = $this->getAccountRoleData();
            $this->render('index', array('aUserRoleData' => $aUserRoleData));
        } else {
			header('Location: /');
            return;
            $config = new TbConfig();
            $configValue = $config->find("sName ='WebSet'");
            $configData = CJSON::decode($configValue->sValue);
            //$configData['usb_key'] = 1;
            $this->render('login',array('flg'=>$configData['usb_key'] ==1 ? 'true':'false'));
        }

    }

    /**
     * 用户认证登录
     */
    public function actionUserLogin()
    {

        if (Yii::app()->request->isPostRequest) {
            $hPost = $this->getParam();
            $hPost->sPassWord    = $this->authcode($hPost->sPassWord, 'DECODE', 'bluedon_edu');
            $userName = trim($hPost->sAccountName);
            $password = trim($hPost->sPassWord);
            //先touch文件
            $useraddress = $this->getIPaddress();
            $this->shellResult("/usr/bin/mkdir -p /tmp/user");
            $shell = " /usr/bin/touch /tmp/user/" . $userName . "_" . $useraddress;
            $this->shellResult($shell);
            //验证
            $ip = $this->getIPaddress();
            $file_name = "rz" . time();
            if (!empty($hPost->actionType)) {
                //短信认证
                $msgReulst = $this->validMsg($userName, $password);
                if ($msgReulst == 0) {
                    $aData['success'] = false;
                    $aData['msg'] = '验证码错误';
                    //记录日志
                    $pData = new stdClass();
                    $pData->sDesc = $userName . "验证码错误";
                    $pData->sRs = "操作失败";
                    $this->saveOperationLog($pData);
                    unset($pData);

                    echo CJSON::encode($aData);
                    Yii::app()->end();
                } else if ($msgReulst == 1) {
                    //记录日志
                    $pData = new stdClass();
                    $pData->sDesc = $userName . "验证码超时";
                    $pData->sRs = "操作失败";
                    $this->saveOperationLog($pData);
                    unset($pData);

                    $aData['success'] = false;
                    $aData['msg'] = '验证码超时';
                    echo CJSON::encode($aData);
                    Yii::app()->end();
                }

            }

            $data = array("sUserName" => $userName, "sPassword" => $password, "sIP" => $ip, "filename" => $file_name, "type" => $hPost->actionType);
            $sCommand = "CMD_AUTHLOGIN|" . CJSON::encode($data);
            $rs = $this->saveCommand($sCommand, '', $ip);
            $aData['success'] = $rs;
            $aData['filename'] = $file_name;
            $aData['username'] = $userName;
            $aData['address'] = $ip;
            echo CJSON::encode($aData);
            Yii::app()->end();
        } else {
            $ip = $this->getIPaddress();
            $sShell = "/usr/bin/sudo /usr/bin/python /usr/local/bluedon/usermanage/authentication_type.py '" . $ip . "' ";
            exec($sShell, $mdata);
            if (!empty($mdata)) {
                $aType = explode('|', $mdata[0]);
                if ($aType[0] == '4') {
                    $this->render('user_authentication_msg', array('type' => $aType[1]));
                    Yii::app()->end();
                }
            }

            $this->render('user_authentication');
        }
    }

    /*
     * 用户认证退出
     */
    public function actionOutLine()
    {
        $aPost = $this->getParam();
        $data = array("sUserName" => $aPost->username, "sIP" => $aPost->address, "filename" => $aPost->filename);
        //$idata = array('iTime'=>time(),'sUserName'=>$aPost->username,'sIP'=>$aPost->sIP,'iAction'=>0,);
        $command = "CMD_AUTH_DOWNLINE|" . CJSON::encode($data);
        $rs = $this->saveCommand($command, '', $aPost->address);
        //$command = "CMD_DEL_AUTHENTICATE_STATUS_FILE|".$aPost->filename;
        //$this->saveCommand($command,'',$aPost->address);
        $aData['success'] = $rs;
        echo CJSON::encode($aData);
        Yii::app()->end();

    }

    public function actionGetDataMsg()
    {
        $hPost = $this->getParam();
        $filename = $hPost->filename;
        $username = $hPost->username;
        $ip = $hPost->address;
        $msg = array(0 => "认证成功,请不要关闭此窗口,否则认证退出", 1 => "认证失败", 2 => "找不到认证策略", 3 => "找不到认证服务器", 4 => "登录ip与该用户所绑定的ip不相符", 5 => "没有开启用户认证", 6 => "找不到该用户");
        $rfile = "/tmp/fifo/" . $filename;
        $aData = array();
        $check = false;
        while (!$check) {
            sleep(2);
            if (file_exists($rfile)) {
                sleep(8);
                $sFileMsg = file_get_contents($rfile);
                $sFileMsg = CJSON::decode($sFileMsg);
                if (isset($sFileMsg['status']) && $sFileMsg['status'] == 0) {
                    $aData['success'] = true;
                    $aData['msg'] = $msg[$sFileMsg['status']];
                    $aData['filename'] = $filename;
                    $aData['username'] = $username;
                    $aData['address'] = $ip;
                    echo CJSON::encode($aData);
                    Yii::app()->end();
                } else {
                    $aData['success'] = false;
                    if (isset($sFileMsg['status'])) {
                        $aData['msg'] = $msg[$sFileMsg['status']];
                        echo CJSON::encode($aData);
                        Yii::app()->end();
                    } else {
                        $aData['msg'] = '认证失败';
                        echo CJSON::encode($aData);
                        Yii::app()->end();
                    }
                }
            } else {
                $check = false;
            }
        }


    }

    //关闭窗口时执行脚本
    public function actionCloseWindow()
    {
        //用户下线
        $model = new TbUsers();
        $model->updateByPk($_SESSION['sUserID'], array("iOnline" => 0));
        $shell = "/usr/bin/userauth/timeout_set_delete.sh " . $this->getIPaddress();
        $this->shellResult($shell);
    }

    /**
     * 保存命令标识符到管道文件
     * @param $sCommand 命令字符串
     */
    public function saveCommand($sCommand = null, $sFileName = '', $ip)
    {
        if (!$sCommand) {
            $aJson['msg'] = "无法获取登录信息！";
            $aJson['success'] = false;
            echo CJSON::encode($aJson);
            Yii::app()->end();
        }
        $fifofile = Yii::app()->params['fifo'];
        $sFile = $sFileName ? $sFileName : $fifofile;
        $fp = fopen($sFile, "w+r+b");
        $bWriter = fwrite($fp, $sCommand . "\n");
        fclose($fp);
        //$bWriter = file_put_contents($sFile, $sCommand."\n");
        if (!$bWriter) {
            $aJson['msg'] = "请求失败！";
            $aJson['success'] = false;
            $aJson['command'] = $sCommand;
            echo CJSON::encode($aJson);
            Yii::app()->end();
        } else {
            return true;
        }

    }

    //获取真是Ip
    function getIPaddress()
    {
        $IPaddress = '';
        if (isset($_SERVER)) {
            if (isset($_SERVER["HTTP_X_FORWARDED_FOR"])) {
                $IPaddress = $_SERVER["HTTP_X_FORWARDED_FOR"];
            } else if (isset($_SERVER["HTTP_CLIENT_IP"])) {
                $IPaddress = $_SERVER["HTTP_CLIENT_IP"];
            } else {
                $IPaddress = $_SERVER["REMOTE_ADDR"];
            }
        } else {
            if (getenv("HTTP_X_FORWARDED_FOR")) {
                $IPaddress = getenv("HTTP_X_FORWARDED_FOR");
            } else if (getenv("HTTP_CLIENT_IP")) {
                $IPaddress = getenv("HTTP_CLIENT_IP");
            } else {
                $IPaddress = getenv("REMOTE_ADDR");
            }
        }
        return $IPaddress;
    }
    
    /**
     * 登陆
     * @remotable
     * @seen  protected\components\UserIdentity.php
     */
    public function actionLoginSystem()
    {
		exit;
        $this->validateCsrfToken();
        //需要考虑的因素有，1，用户的状态，2，系统最大并发管理数
        $lModel             = new TbAccount();
        $hPost              = $this->getParam(); //提交的参数
        $sAccountName       = trim($hPost->sAccountName);
        $now                = time();
        $sPassWord          = $hPost->sPassWord;
        $sPassWord          = $this->authcode($sPassWord, 'DECODE', 'bluedon_edu');
        $sCode              = $hPost->sCode;            //获取的验证码
        $sGetCode           = $this->getVerifyCode();   //校验的验证码
        $success            = false;
        $aJson              = array();
        //获取系统配置
        $configValue        = TbConfig::model()->find("sName ='WebSet'");
        $configData         = CJSON::decode($configValue->sValue);
        //是否被锁      true为已经被锁      //iStatus 2禁用   4启用
        $bLock              = $this->Selecthandlock($sAccountName);
        //登录失败次数   true为超过次数
        $aLogins            = $this->getNumlogin($sAccountName, $configData['iMaxLoginNumber'], $configData['iTimeOut']);
        $bLoginNum          = $aLogins['maxlogin'];
        $iLoginCount        = $aLogins['count'];
        //判断用户是否过期
        if(TbAccount::model()->IsExpired($sAccountName)){
            $aJson ['msg'] = '登录失败,该用户已经过期';
            //写日志
            $logindata = array("iUserId" => $sAccountName, "iLoginTime" => $now, "sIp" => Yii::app()->request->userHostAddress, "sStatus" => 2, "sContent" => $aJson ['msg']);
            $this->AddLoginStatus($logindata);
            $this->showMessage(false, '该用户已经过期,请联系管理员');
        }
        //最大并发管理数
        $timeout_count      = Tbtimeout::model()->count();
        if (isset($configData['iMaxConcurrent']) && !empty($configData['iMaxConcurrent'])) {
            if ($timeout_count > $configData['iMaxConcurrent'] - 1) {
                $this->showMessage(false, '登录用户已经达到最大并发管理值，请等待');
            }
        }
        //单用户限制 限制一个用户多少个IP同时登陆
        $same_time  = Tbtimeout::model()->getOnlineNum($sAccountName);
        if ($same_time >= $configData['iLoginLimit']) {
            $this->showMessage(false, '单用户只能' . $configData['iLoginLimit'] . '个IP同时登陆');
        }
        if ($bLock || $bLoginNum) {
            if ($bLock) {
                $aJson ['msg'] = '用户被禁用';
            } else {
                $aJson ['msg'] = '用户已经被锁定 请' . $configData['iTimeOut'] . '分钟后再重试';
                $this -> getLoginAbnor('用户'.$sAccountName.'登录失败次数超过登入失败重试数');
            }
            //写日志
            $logindata = array("iUserId" => $sAccountName, "iLoginTime" => $now, "sIp" => Yii::app()->request->userHostAddress, "sStatus" => 2, "sContent" => $aJson ['msg']);
            $this->AddLoginStatus($logindata);
            //当用户锁住的时候需要更新用户表的状态  3为用户登入失败数锁
            if ($bLock == 0) {
                $this->updateistatus($sAccountName, 3); //用户登入失败数锁
            }
        } else {
            if (strtolower($sCode) != strtolower($sGetCode)) {
                $aJson ['msg'] = '验证码错误';
                $aJson ['code'] = true;
                $logindata = array("iUserId" => $sAccountName, "iLoginTime" => $now, "sIp" => Yii::app()->request->userHostAddress, "sStatus" => 2, "sContent" => "验证码错误");
                $this->AddLoginStatus($logindata);
            } else {
                //验证用户名密码
                $identity = new UserIdentity($sAccountName, $sPassWord);
                if ($identity->authenticate()) {
                    //判断用户是否需要USB_KEY登录
                    $sUserPin = $identity->getState('usb_pin');
                    if(!empty($sUserPin)){
                        $aJson ['code'] = 9;
                        echo CJSON::encode($aJson);
                        Yii::app()->end();
                    }
                    $success = $this->identity_succ($hPost,$identity);
                } else {
                    // $aJson['debug_erro'] = $hPost;
                    if($identity->errorCode == 1){
                        $logindata = array("iUserId" => $sAccountName, "iLoginTime" => $now, "sIp" => Yii::app()->request->userHostAddress, "sStatus" => 2, "sContent" => "登录失败 账号不存在");
                    }elseif($identity->errorCode == 2){
                        $logindata = array("iUserId" => $sAccountName, "iLoginTime" => $now, "sIp" => Yii::app()->request->userHostAddress, "sStatus" => 2, "sContent" => "登录失败 密码输入错误");
                    }else{
                        $logindata = array("iUserId" => $sAccountName, "iLoginTime" => $now, "sIp" => Yii::app()->request->userHostAddress, "sStatus" => 2, "sContent" => "登录失败 账号或密码输入错误");
                    }
                    $this->AddLoginStatus($logindata);
                    $aJson ['msg'] = '账号或密码错误，请输入正确的账号或密码';
                    $aJson ['msgs'] = $identity->errorMessage;
                }
            }
        }
        //iIllegalLogin非法登入告警     iLoginAlarm重试多次告警
        $configData['iIllegalLogin'] = isset($configData['iIllegalLogin']) ? $configData['iIllegalLogin'] : 0;
        /*if ($configData['iIllegalLogin'] && !$this->isAllowIp() ||
                (($iLoginCount && $configData['iLoginAlarm'] && $configData['iLoginAlarm'] >= $iLoginCount)) ){
            $publishData =  CJSON::encode(array(
                'username' => $sAccountName,
                'ip' => Yii::app()->request->userHostAddress,
                'logintime' => $now,`
                'status' => $success ? '1' : '0',
                'type' => 'login',
            ));
            Yii::app()->redis->getClient()->publish('bdaudit_exception_behavior', $publishData);
        }*/
        //判断角色权限
        $_SESSION['isAuth'] = false;
        /*$iUserId = Yii::app()->user->getId();
        $sysUser = array(
                Yii::app()->params['sysUserId'],
                Yii::app()->params['auditUserId'],
                Yii::app()->params['adminUserId'],
            );
        if ($sAccountName != Yii::app()->params['rootSys'] && !in_array($iUserId, $sysUser)) {
            $exist=Yii::app()->db->createCommand("SHOW TABLES LIKE '{{tbaccount_permission}}'")->queryAll(); //查询表是否存在
            if($exist){
                $_SESSION['isAuth'] = true;
                
                //获取当前用户的所有权限
                $userInfo = $lModel->find(array(  
                                        'select'=>'iUserId,sLoginAccount,iOperationUserId',  
                                        'condition'=>'sLoginAccount=:sLoginAccount',  
                                        'params'=>array(':sLoginAccount'=>$sAccountName) 
                                    ));
                //非内置管理员用户需要验证权限，参照配置文件params/sysUserId、auditUserId、adminUserId
                if ($userInfo['attributes']['iOperationUserId'] > 1) { 
                    //获取权限
                    $user_permission = TbAccountPermission::model()->findAll("iUserId=:iUserId" , array(":iUserId"=>$userInfo['attributes']['iUserId']));
                    $user_permission = CJSON::decode(CJSON::encode($user_permission));
                    $user_permission = array_reduce($user_permission, create_function('$v,$w', '$v[$w["iNavId"]]=$w;return $v;')); 
                    $_SESSION['user_permission'] = $user_permission;  
                }
            }
        }*/

        //把角色ID写到session里面
        $lc = new CDbCriteria();
        $lc ->condition= "sLoginAccount = :sLoginAccount";
        $lc ->params=array(":sLoginAccount"=>$sAccountName);
        $sRole = $lModel->find($lc)->sRole;
        Yii::app()->session['sRole']=$sRole;
        $aJson ['success'] = $success;
        echo CJSON::encode($aJson);
        Yii::app()->end();
    }

	/**
     * 登陆
     * @remotable
     * @seen  protected\components\UserIdentity.php
     */
    public function actionLoginSystemWaf()
    {
        //需要考虑的因素有，1，用户的状态，2，系统最大并发管理数
        $lModel             = new TbAccount();
        $hPost              = $this->getParam(); //提交的参数
        $sAccountName       = trim($hPost->sAccountName);
        $now                = time();
        $sPassWord          = $hPost->sPassWord;
        $sPassWord          = $this->authcode($sPassWord, 'DECODE', $sAccountName, 5);
        $sCode              = $hPost->sCode;            //获取的验证码
        $sGetCode           = $this->getVerifyCode();   //校验的验证码
        $success            = false;
        $aJson              = array();
        //获取系统配置
        $configValue        = TbConfig::model()->find("sName ='WebSet'");
        $configData         = CJSON::decode($configValue->sValue);
        //是否被锁      true为已经被锁      //iStatus 2禁用   4启用
        $bLock              = $this->Selecthandlock($sAccountName);
        //登录失败次数   true为超过次数
        $aLogins            = $this->getNumlogin($sAccountName, $configData['iMaxLoginNumber'], $configData['iTimeOut']);
        $bLoginNum          = $aLogins['maxlogin'];
        $iLoginCount        = $aLogins['count'];
               
        //最大并发管理数
        $timeout_count      = Tbtimeout::model()->count();
        if (isset($configData['iMaxConcurrent']) && !empty($configData['iMaxConcurrent'])) {
            if ($timeout_count > $configData['iMaxConcurrent'] - 1) {
				$result['info'] = '登录用户已经达到最大并发管理值，请等待';
				$result['code'] = 'F';
				echo CJSON::encode($result);
				Yii::app()->end();
            }
        }
        //单用户限制 限制一个用户多少个IP同时登陆
        $same_time  = Tbtimeout::model()->getOnlineNum($sAccountName);
        if ($same_time >= $configData['iLoginLimit']) {
			$result['info'] = '单用户只能' . $configData['iLoginLimit'] . '个IP同时登陆';
			$result['code'] = 'F';
			echo CJSON::encode($result);
			Yii::app()->end();
        }
        if ($bLock || $bLoginNum) {
            $result['code'] = 'F';
            if ($bLock) {
                $result['info'] = '用户被禁用';
            } else {
                $result['info'] = '用户已经被锁定 请' . $configData['iTimeOut'] . '分钟后再重试';
            }
            //写日志
            $logindata = array("iUserId" => $sAccountName, "iLoginTime" => $now, "sIp" => Yii::app()->request->userHostAddress, "sStatus" => 2, "sContent" => $result['info']);
            $this->AddLoginStatus($logindata);
            //当用户锁住的时候需要更新用户表的状态  3为用户登入失败数锁
            if ($bLock == 0) {
                $this->updateistatus($sAccountName, 3); //用户登入失败数锁
            }
        } else {
            if (false) {
            } else {
                //验证用户名密码
                $identity = new UserIdentity($sAccountName, $sPassWord);
                if ($identity->authenticate()) {
                    //判断用户是否需要USB_KEY登录
                    $sUserPin = $identity->getState('usb_pin');
                    if(!empty($sUserPin)){
                        $aJson ['code'] = 9;
                        echo CJSON::encode($aJson);
                        Yii::app()->end();
                    }
                    $success = $this->identity_succ($hPost,$identity);
					$result['info'] = '登陆成功';
					$result['code'] = 'T';
                } else {
                    $aJson['debug_erro'] = $hPost;
                    if($identity->errorCode == 1){
                        $logindata = array("iUserId" => $sAccountName, "iLoginTime" => $now, "sIp" => Yii::app()->request->userHostAddress, "sStatus" => 2, "sContent" => "登录失败 账号不存在");
                    }elseif($identity->errorCode == 2){
                        $logindata = array("iUserId" => $sAccountName, "iLoginTime" => $now, "sIp" => Yii::app()->request->userHostAddress, "sStatus" => 2, "sContent" => "登录失败 密码输入错误");
                    }else{
                        $logindata = array("iUserId" => $sAccountName, "iLoginTime" => $now, "sIp" => Yii::app()->request->userHostAddress, "sStatus" => 2, "sContent" => "登录失败 账号或密码输入错误");
                    }
                    $this->AddLoginStatus($logindata);
                    //$aJson ['msg'] = '账号或密码错误，请输入正确的账号或密码';
                    //$aJson ['msgs'] = $identity->errorMessage;
					
					$result['info'] = '账号或密码错误，请输入正确的账号或密码';
					$result['code'] = 'F';
                }
            }
        }
        //iIllegalLogin非法登入告警     iLoginAlarm重试多次告警
        $configData['iIllegalLogin'] = isset($configData['iIllegalLogin']) ? $configData['iIllegalLogin'] : 0;
        /*if ($configData['iIllegalLogin'] && !$this->isAllowIp() ||
                (($iLoginCount && $configData['iLoginAlarm'] && $configData['iLoginAlarm'] >= $iLoginCount)) ){
            $publishData =  CJSON::encode(array(
                'username' => $sAccountName,
                'ip' => Yii::app()->request->userHostAddress,
                'logintime' => $now,`
                'status' => $success ? '1' : '0',
                'type' => 'login',
            ));
            Yii::app()->redis->getClient()->publish('bdaudit_exception_behavior', $publishData);
        }*/
        //把角色ID写到session里面
        $lc = new CDbCriteria();
        $lc ->condition= "sLoginAccount = :sLoginAccount";
        $lc ->params=array(":sLoginAccount"=>$sAccountName);
        $sRole = $lModel->find($lc)->sRole;
        Yii::app()->session['sRole']=$sRole;
        //$aJson ['success'] = $success;
        echo CJSON::encode($result);
        Yii::app()->end();
    }

	
    public function actionCheckUsbkey(){
        $hPost                      = $this->getParam(); //提交的参数
        $aJson                      = array();
        $account_model              = new TbAccount();
        $criteria                   = new CDbCriteria();
        $criteria->condition        = 'sLoginAccount=:username';
        $criteria->params           = array(':username'=>$hPost->sAccountName);
        $accountData                = $account_model->find($criteria);
        $sAccountName               = trim($hPost->sAccountName);
        //认证
        $hPost->epassy = $this->authcode($hPost->epassy, 'DECODE', 'bluedon_fw');
        $aEpassy = explode('|', $hPost->epassy);
        //$aEpassy[0] = 'bluedon';
        if (!empty($aEpassy) && $aEpassy[0] != $accountData['usb_pin']) {
            $aJson ['msg'] = 'USB KEY认证失败';
            $aJson ['success'] = false;
            Yii::app()->session->clear(); // 移除所有session变量，然后，调用
            Yii::app()->session->destroy(); //移去存储在服务器端的数据。
        } else {
            $aJson ['msg']  = 'USB KEY认证成功';
            $sPassWord      = $hPost->sPassWord;
            $identity       = new UserIdentity($sAccountName, $sPassWord);
            if ($identity->authenticate()) {
            }
            $hPost->sRole   = $accountData->sRole;
            $success        = $this->identity_succ($hPost,$identity);
            $aJson ['success'] = $success;
        }

        $sessionid = Yii::app()->session->sessionID;
        $exptime = '';
        if (empty($infos['iTimeOut'])) {
            $infos['iTimeOut'] = 30;
            $exptime = time() + $infos['iTimeOut'] * 60;
        } else {
            $exptime = time() + $infos['iTimeOut'] * 60;
        }
        $inssql             = "insert into m_tbsession (username ,iSessionId,exptime) VALUES ('" . $hPost->sAccountName . "','" . $sessionid . "','" . $exptime . "')";
        Yii::app()->db->createCommand($inssql)->execute();
        //把角色ID写到session里面
        $lc                 = new CDbCriteria();
        $lModel             = new TbAccount();
        $lc ->condition     = "sLoginAccount = :sLoginAccount";
        $lc ->params        = array(":sLoginAccount"=>$sAccountName);
        $sRole              = $lModel->find($lc)->sRole;
        Yii::app()->session['sRole']=$sRole;
        $config             = new TbConfig();
        $info               = $config->find("sName='WebSet'");
        $infos              = CJSON::decode($info['sValue']);
        $_SESSION['username'] = $sAccountName;
        echo CJSON::encode($aJson);
        Yii::app()->end();
    }

    /*
     * @param $hPost    Object  页面传递过来的数据对象
     * @param $identity Object
     *
     */
    /*private function getUsbkey($hPost,$identity){
        //认证
        $hPost->epassy = $this->authcode($hPost->epassy, 'DECODE', 'bluedon_fw');
        $aEpassy = explode('|', $hPost->epassy);
        $sUserPin = $identity->getState('usb_pin');
        if (!empty($sUserPin)) {

            if (!empty($aEpassy) && $aEpassy[0] != $sUserPin) {
                $aJson ['msg'] = 'USB KEY认证失败';
                $aJson ['code'] = true;
                Yii::app()->session->clear(); // 移除所有session变量，然后，调用
                Yii::app()->session->destroy(); //移去存储在服务器端的数据。
            } else {
                $aJson ['msg'] = 'USB KEY认证成功';
                $aJson ['success'] = true;
            }
            $logindata = array("iUserId" => $hPost->sAccountName, "iLoginTime" => time(), "sIp" => Yii::app()->request->userHostAddress, "sStatus" => 2, "sContent" => "KEY认证失败");
            $a = $this->AddLoginStatus($logindata);
            if ($aJson ['code'] == true) {
                echo CJSON::encode($aJson);
                Yii::app()->end();
            }

        }
    }*/

    private function identity_succ($hPost,$identity){
        Yii::app()->user->login($identity);
        if(!isset($hPost->sRole) && !empty($hPost->sAccountName)){
            $account_model              = new TbAccount();
            $criteria                   = new CDbCriteria();
            $criteria->condition        = 'sLoginAccount=:username';
            $criteria->select           = 'sRole';
            $criteria->params           = array(':username'=>$hPost->sAccountName);
            $hPost->sRole               = $account_model->find($criteria)->sRole;
        }
        $logindata     = array("iUserId" => $hPost->sAccountName, "iLoginTime" => time(), "sIp" => Yii::app()->request->userHostAddress, "sStatus" => 1, "sContent" => "登录成功","sRole"=>$hPost->sRole);
        $this->AddLoginStatus($logindata);
        $aJson ['msg'] = '操作成功';
        $success       = true;
        $sSQL          = "update m_tbloginlog set sStatus='3' where iLoginTime >  " . (time() - Yii::app()->params['iLoginTime']) . " and iLoginTime < " . time() . " and sStatus='2' and iUserId = '$hPost->sAccountName' ";
        Yii::app()->db_log->createCommand($sSQL)->execute();
        $this->updateistatus($hPost->sAccountName, 4);
        $this->updateionline($hPost->sAccountName, 1, 'name');
        /**
         * 添加过期时间
         */
        $config = new TbConfig();
        $info = $config->find("sName='WebSet'");
        $infos = CJSON::decode($info['sValue']);
        $_SESSION['username'] = $hPost->sAccountName;
        /*
         * 20160824  添加至TIMEOUT表
         */
        $timeout_model = new Tbtimeout();
        $config = new TbConfig();
        $sessionid = Yii::app()->session->sessionID;
        $iTimeOut = $infos['iTimeOut'];
        $timeout_model->iUserId = $this->getAccountId($hPost->sAccountName);
        $timeout_model->username = $hPost->sAccountName;
        $timeout_model->iSessionId = $sessionid;
        $timeout_model->iSessionTimeout = $infos['iTimeOut'] ? $infos['iTimeOut'] * 60 + time() : time() + $iTimeOut * 60;
        $timeout_model->sIp = $this->getIPaddress();
        $timeout_model->expireTime = time() + $iTimeOut * 60;
        $r = $timeout_model->save();
        return $success;
    }



    /**
     * 退出
     * @remotable
     */
    public function actionLogoutSys()
    {
        /***
         * 操作日志
         */
        $sDesc = "退出系统";
        $pData = new stdClass();
        $pData->sDesc = $sDesc;
        $loginuserid = Yii::app()->user->getId();
        $pData->sRs="操作成功";
        $this->saveOperationLog($pData);
        //TIMEOUT删除数据
        $timeout_model              = new Tbtimeout();
        $sessionid                  = Yii::app()->session->sessionID;
        $timeout_model->deleteAll("iSessionId=:iSessionId",array(':iSessionId'=>$sessionid));


        Yii::app()->user->logout();
        $this->updateionline($loginuserid, 0, 'id');
        Yii::app()->session->clear(); // 移除所有session变量，然后，调用
        Yii::app()->session->destroy(); //移去存储在服务器端的数据。
        $aJson = array();
        $aJson ['success'] = true;
        $aJson ['msg'] = '操作成功';
        echo CJSON::encode($aJson);
        Yii::app()->end();
    }

    public function actionInstallEPass()
    {
        $this->render('usbkey/install');
    }
    /**
     * This is the action to handle external exceptions.
     */
    public function actionError()
    {

        if ($error = Yii::app()->errorHandler->error) {
            if (Yii::app()->request->isAjaxRequest) {
                $aMgs = array('msg' => $error['message'], 'success' => false);
                echo CJSON::encode($aMgs);
                Yii::app()->end();
            } else {
                if (YII_DEBUG) {
                    $this->render('error_old', $error);
                } else {

                    $this->render('error', $error);
                }
            }
        }

    }

    private function getVerifyCode()
    {
        $captch = new CCaptchaAction($this, 'captcha'); // captcha 一定要与上面定义的一样。
        return $captch->getVerifyCode();
    }

    /**
     * 用户对应的角色
     */
    private function getAccountRoleData()
    {
        $hModel = new TbAccount();
        $rModel = new TbRole();
        $loginuserid = Yii::app()->user->getId();
        $loginuserdata = $hModel->find('iUserId=:iUserId', array(':iUserId' => $loginuserid));
        $loginroleid = $loginuserdata['sRole'];
        $loginroledata = $rModel->find('iRoleId=:iRoleId', array(':iRoleId' => $loginroleid));

        $config = new TbConfig();
        $info = $config->find("sName='PasswordSecurity'");
        $setting = CJSON::decode($info['sValue']);

        $aJson['success'] = true;
        $aJson['sRole'] = $loginroleid;
        $aJson['sRoleName'] = " 拥有角色有：" . $loginroledata['sRoleName'];
        $aJson['dSeriveDate'] = gmdate("Y-m-d H:i:s", time() + gmdate("Z"));
        $aJson['sUserName'] = Yii::app()->user->getName();
        $aJson['iUpdatePwd'] = $loginuserdata['iUpdatePwd'];
        $aJson['setting'] = $setting;

        //菜单树
        $hTree = new TbNavTree();
        $c = new CDbCriteria();
        if (Yii::app()->user->getState('sLoginAccount') != Yii::app()->params['rootSys']) {
            if($_SESSION['isAuth']) { 
                $c->with = array('account_permession');
                $c->addCondition("account_permession.iUserId = :iUserId AND account_permession.iView=1");
                $c->params[':iUserId'] =  $loginuserid;
            } else {
                $c->with = array('rolenavtree');
                $c->addCondition("rolenavtree.iRoleId = :iRoleId");
                $c->params[':iRoleId'] =  $loginroleid;
            }
        }

        $c->order = "t.iSort asc,t.iNavId asc";
        $c->addCondition("bVisible=1");
        $aTreeList = $hTree->findAll($c);
        $aNavTree = array();
        foreach ($aTreeList as $t) {
            //第一层菜单
            if ($t->iParentId == 0) {
                $aItem = array(
                    'title' => $t->sName,
                    'icons' => $t->sIcon,
                    'url' => $t->sUrl,
                    'child' => array(),
                );

                foreach ($aTreeList as $second) {
                    if ($t->iNavId == $second->iParentId) {
                        $aSecond = array(
                            'url' => $second->sUrl,
                            'title' => $second->sName,
                            'child' => array(),
                        );
                        //第三层菜单
                        foreach ($aTreeList as $third) {
                            if ($second->iNavId == $third->iParentId) {
                                $third = array(
                                    'url' => $third->sUrl,
                                    'title' => $third->sName,
                                );
                                $aSecond['child'][] = $third;
                            }
                        }

                        $aItem['child'][] = $aSecond;
                    }
                }
                array_push($aNavTree, $aItem);
            }
        }
        $aJson['navTree'] = $aNavTree;
        return $aJson;


    }

    /**
     * 用户拥有多少个角色
     * @remotable
     */
    private function getUserRoleData()
    {
        $hModel = new TbRole();
        $c = new CDbCriteria();
        $c->condition = 'iRoleId in (select iRoleId from m_tbroleaccount where iUserId=:iUserId)';
        $c->params[':iUserId'] = Yii::app()->user->getId();
        $hData = $hModel->findAll($c);
        $aData = array();
        foreach ($hData as $k => $v) {
            array_push($aData, $v->sRoleName);
        }
        $aJson['success'] = true;
        $aJson['sRoleName'] = " 拥有角色有：" . implode(',', $aData) . "　";
        $aJson['iRoleName'] = implode(',', $aData) . "　";
        $aJson['dSeriveDate'] = gmdate("Y-m-d H:i:s", time() + gmdate("Z"));
        $aJson['sUserName'] = Yii::app()->user->getName();
        return $aJson;
    }

    /**
     * 扫描x分钟内用户登录失败的次数
     * param  $userid           int  用户ID
     * param  $iMaxLoginNumber  int  系统最大登录次数
     * param  $iTimeOut         int  超时时间 分钟为单位
     * return array             array('maxlogin'=>boolean,'count'=>int)
     *                          数组第一个参数为代表该用户是否超过最大登录次数 true代表超过  false代表并没有
     *                          数组第二个参数为在超时时间内的登录次数
     */
    private function getNumlogin($userid, $iMaxLoginNumber = false, $iTimeOut = false)
    {
        $hModel = new TbLoginLog();
        $now = time();
        //登入失败重试数
        $iMaxLoginNumber = $iMaxLoginNumber ? $iMaxLoginNumber : Yii::app()->params['iLoginNum'];
        $nowLast = $iTimeOut ? $now - $iTimeOut * 60 : $now - Yii::app()->params['iLoginTime'];
        $c = new CDbCriteria();
        $c->condition = " iLoginTime > $nowLast and iLoginTime < $now and sStatus='2' and iUserId = :userid";
        $c->params      = array(':userid'=>$userid);
        $c->select      = 'iUserId';
        $hData = $hModel->findAll($c);
        return array('maxlogin' => count($hData) > $iMaxLoginNumber - 1 , 'count' => count($hData));
    }

    /**
     * 查看是否有手动加锁
     * 　锁上返为true;
     */
    private function Selecthandlock($userid)
    {
        $hModel         = new TbAccount();
        $c              = new CDbCriteria();
        $c->condition   = "iStatus = '2' and sLoginAccount = :userid";
        $c->params      = array(':userid'=>$userid);
        $hData          = $hModel->findAll($c);
        return count($hData);

    }



    public function getAccountId($username)
    {
        $hModel = new TbAccount();
        $criteria = new CDbCriteria();
        $criteria->select = 'iUserId';
        $criteria->condition = 'sLoginAccount=:username';
        $criteria->params = array(':username' => $username);
        $hData = $hModel->find($criteria);
        return $hData->iUserId;
    }

    /**
     *更新m_tbaccount的istatus状态
     * @param $data
     * @return bool
     *
     */
    private function updateistatus($username, $iStatus)
    {
        $sSQL = "update m_tbaccount set iStatus = :iStatus where sLoginAccount = :username";
        Yii::app()->db->createCommand($sSQL)->execute(array(':username'=>$username,':iStatus'=>$iStatus));
    }

    private $iloginLogId ;
    private function AddLoginStatus($data)
    {
        $userInfo = TbAccount::model()->find("sLoginAccount=:sLoginAccount" , array(":sLoginAccount" => $data['iUserId'] ));
        $userInfo = CJSON::decode(CJSON::encode($userInfo));
        if($userInfo['iOperationUserId'] > 0){
            $message = '用户'.$data['iUserId'].$data['sContent'];
            $this->getLoginAbnor($message, $userInfo['iOperationUserId']);
        }

        $hModel                 = new TbLoginLog();
        $this->iloginLogId      = $data['iloginLogId'] = $hModel->getGId();
        //判断该ID是否已经存在于LOG表,存在则重新获取
        $i                      = 0 ;
        while(!$this->checkSameLogId($this->iloginLogId)){
            $i++;
            $this->iloginLogId  = TbLoginLog::model()->getGId();
            if($i>10000) return false;
        }
        $data['iloginLogId']    = $this->iloginLogId;
        $hModel->attributes = $data;
        if ($hModel->save()) {
            return true;
        } else {
            return false;
        }
    }
    /*
     * @param   $iloginLogId int
     * @RETURN  boolean  false   已存在该ID
     *          boolean  true    不存在该ID
     */
    private function checkSameLogId($iloginLogId){
        $iloginLogId    = intval($iloginLogId);
        $result         =   TbLoginLog::model()->count("iloginLogId=:iloginLogId",array(":iloginLogId"=>$iloginLogId));
        if($result > 0){
            return false;
        }else{
            return true;
        }
    }

    private function updateionline($login, $param, $field)
    {
        if ($field == 'id') {
            $sSQL = "update m_tbaccount set iOnline = '$param' where iUserId = '$login'";
        } else {
            $sSQL = "update m_tbaccount set iOnline = '$param' where sLoginAccount = '$login'";
        }
        Yii::app()->db->createCommand($sSQL)->execute();

    }


    public function actionTouchFile()
    {

        if (Yii::app()->request->isPostRequest) {
            $hPost          = (array)$this->getParam();
            if(!is_dir("/tmp/user")){
                $this->shellResult("/usr/bin/sudo /usr/bin/mkdir -p /tmp/user");
            }
            if (!empty($hPost['username']) && !empty($hPost['address'])) {
                $exist_file     = "/tmp/downuser/".$hPost['username'] . "_" . $hPost['address']."_false";
                if(file_exists($exist_file)){
                    $this->shellResult("/usr/bin/sudo /usr/bin/rm -f ".$exist_file);
                    $this->showMessage(false,'用户已经下线,请重新登录');
                }else{
                    $shell      = "/usr/bin/sudo /usr/bin/touch /tmp/user/" . $hPost['username'] . "_" . $hPost['address'];
                    $this->shellResult($shell);
                }
            }
        }
    }


    /**
     * -1 为超时，1是成功，0为失败
     * @return int
     */
    private function validMsg($sendNum, $iNum)
    {
        //判断手机号码格式
        if (!preg_match('/^(((\+86)|(86)|(086))?1\d{10})$/', $sendNum)) {
            //记录日志
            $pData = new stdClass();
            $pData->sDesc = $sendNum . "手机号码格式输入不正确";
            $pData->sRs = "操作失败";
            $this->saveOperationLog($pData);
            unset($pData);
            $this->showMessage(false, '手机号码格式输入不正确');
        }
        if (!preg_match('/^\d{6}$/', $iNum)) {
            //记录日志
            $pData = new stdClass();
            $pData->sDesc = $sendNum . "验证码格式输入不正确";
            $pData->sRs = "操作失败";
            $this->saveOperationLog($pData);
            unset($pData);
            $this->showMessage(false, '验证码格式输入不正确');
        }
        $SQL = "SELECT * FROM `m_tbmobile_message`  A WHERE msg_time=(SELECT MAX(msg_time) FROM `m_tbmobile_message` WHERE sendNum='" . $sendNum . "' AND iNum='" . $iNum . "');";
        $mobile_data = Yii::app()->db->createCommand($SQL)->queryRow();
        if (!empty($mobile_data)) {
            $msg_time = $mobile_data['msg_time'];
            //验证是否超时
            if (time() - $msg_time < $this->limit_time * 60) {
                return -1;
            } else {
                return 1;
            }
        } else {
            return 0;
        }
    }

    /**
     * -1 为超时，1是成功，0为失败
     * @return int
     */
    /* private function validMsg_SQLData($sendNum,$iNum){

         $mobile_model                   = new TbmobileMessage();
         $criteria                       = new CDbCriteria;
         $criteria->select               = 'msg_time';  // 只选择 'sendNum' 列
         $criteria->addCondition('sendNum=:sendNum');
         $criteria->addCondition('iNum=:iNum');
         $criteria->params               = array(':sendNum'=>$sendNum,':iNum'=>$iNum);
         $mobile_data                    = $mobile_model->find($criteria); // $params 不需要了
         if(!empty($mobile_data)){
             $msg_time                   = $mobile_data->msg_time;
             //验证是否超时
             if(time()-$msg_time < $this->limit_time*60){
                 return -1;
             }else{
                 return 1;
             }
         }else{
             return 0;
         }
     }*/

    /**
     * 百信通 短信接口
     */
    public function actionSendMsgBXT()
    {
        $hPost = $this->getParam(); //提交的参数
        $rest = new RESTClient();
        $rest->initialize(array('server' => 'http://124.173.80.214:9999/')); //注意内容要有【蓝盾防火墙上网认证系统】这样的格式
        $rest->set_header('Content-Type', 'multipart/form-data');
        $sTime = date("YmdHis");
        $sAccout = 'lv002-0801';
        $sPasswd = 'bluedon201607';
        $sign = md5($sAccout . $sPasswd . $sTime);
        $aPost = array('action' => 'send', 'userid' => 28, 'timestamp' => $sTime, 'sign' => $sign, 'mobile' => $hPost->sTel, 'content' => '
【蓝盾防火墙上网认证系统】您此次的上网验证码为：' . $this->getMsgNum($hPost->sTel) . '。有效时间为3分钟，请保密并确认是本人操作！', 'sendTime' => '', 'extno' => '');
        $result = $rest->post('v2sms.aspx', $aPost, 'xml');
        $aJson = array();
        if ($result['message'] == 'ok') {
            $aJson ['success'] = true;
            $aJson ['msg'] = '发送短信成功';
        } else {
            $aJson ['success'] = false;
            $aJson ['msg'] = '发送短信失败';
            Yii::log($result);
        }
        echo CJSON::encode($aJson);
        Yii::app()->end();
    }

    /**
     * 吉信通 短信接口
     */
    public function actionSendMsgJXXT()
    {
        $hPost = $this->getParam(); //提交的参数
        $rest = new RESTClient();
        //http://service.winic.org/sys_port/gateway/?id=userid&pwd=password&to=接收短信手机号码&content=短信内容&time= //注意内容要是GB2312
        $rest->initialize(array('server' => 'http://service.winic.org/'));
        $sTime = date("YmdHis");
        $sAccout = 'bluedon';
        $sPasswd = 'bluedon123';
        $aPost = array('id' => $sAccout, 'pwd' => $sPasswd, 'to' => $hPost->sTel, 'content' => mb_convert_encoding('【蓝盾防火墙上网认证系统】您此次的上网验证码为：' . $this->getMsgNum($hPost->sTel) . '。有效时间为3分钟，请保密并确认是本人操作！', 'GB2312', 'UTF8'), 'time' => '');
        $result = $rest->get('sys_port/gateway/', $aPost);
        $result = explode('/', $result);
        $aJson = array();
        if ($result[0] == '000') {
            $aJson ['success'] = true;
            $aJson ['msg'] = '发送短信成功';
        } else {
            $aJson ['success'] = false;
            $aJson ['msg'] = '发送短信失败';
            Yii::log($result);
        }
        echo CJSON::encode($aJson);
        Yii::app()->end();
    }

    private function getMsgNum($phone)
    {
        //判断手机号码格式
        if (!preg_match('/^(((\+86)|(86)|(086))?1\d{10})$/', $phone)) {
            $this->showMessage(false, '手机号码格式输入不正确');
        }
        //记录日志
        $pData = new stdClass();
        $pData->sDesc = $phone . "短信认证获取验证码";
        $pData->sRs = "操作成功";
        $this->saveOperationLog($pData);

        //获取验证码  先判断手机号码是否超过访问限制
        $day_limit_time = 24 * 3600;
        $limit_num = 100;
        $SQL = "SELECT COUNT(*) AS num FROM `m_tbmobile_message` WHERE sendNum='" . $phone . "' AND msg_time > UNIX_TIMESTAMP()-" . $day_limit_time;
        $phone_data = Yii::app()->db->createCommand($SQL)->queryRow();
        if ($phone_data['num'] > $limit_num) $this->showMessage(false, '单个号码每天只能发送100次短信');
        //判断IP地址地址访问是否超过限制
        $sIp = ip2long($this->getIPaddress());
        $SQL = "SELECT COUNT(*) AS num FROM `m_tbmobile_message` WHERE sIp='" . $sIp . "' AND msg_time > UNIX_TIMESTAMP()-" . $day_limit_time;
        $ip_data = Yii::app()->db->createCommand($SQL)->queryRow();
        if ($ip_data['num'] > $limit_num) $this->showMessage(false, '单个IP每天只能发送100次短信');
        //判断5每分钟访问次数是否超过限制
        $second_time = 60 * 5;
        $SQL = "SELECT COUNT(*) AS num FROM `m_tbmobile_message` WHERE msg_time > UNIX_TIMESTAMP()-" . $second_time;
        $second_data = Yii::app()->db->createCommand($SQL)->queryRow();
        if ($second_data['num'] > $limit_num) $this->showMessage(false, '每分钟只能发送100次短信');

        $iNum = mt_rand(100000, 999999);
        $mobile_model = new TbmobileMessage();
        $mobile_model->sendNum = $phone;
        $mobile_model->iNum = $iNum;
        $mobile_model->msg_time = time();
        $mobile_model->sIp = ip2long($this->getIPaddress());
        $mobile_model->save();
        return $iNum;
        /*$mobile_data    = $mobile_model->find('sendNum=:sendNum',array(':sendNum'=>$phone));
        if(empty($mobile_data)){
        }else{
            $mobile_model->updateAll(array('iNum'=>$iNum,'msg_time'=>time()),'sendNum=:sendNum',array(':sendNum'=>$phone));
        }*/

    }
    
    /**
     * 是否在允许的IP段中，见系统:web控制配置
     * @return boolean
     */
    private function isAllowIp(){
        $tUrl = Yii::app()->request->url;
        $urls  = explode("/",$tUrl);
        $clientip = $this->get_client_ip6();
        $ip1 = false;
        $ip2 = false;
        $ip3 = false;
        if(strtolower($urls[1])== 'site'){
            $actionarr = array("userlogin.htm5","userlogin","getdatamsg","getdatamsg.htm5","captcha","captcha.htm5");
            if( in_array(strtolower($urls[2]),$actionarr)){
                return true;
            }
        }
        if(!empty($clientip)){
            $hModel = new TbConfig();
            $info=$hModel->find("sName='WebSet'");
            $data=CJSON::decode($info['sValue']);
            $maskstr1 ='';
            $maskstr2 ='';
            $maskstr3 ='';
            $ipstr1 ='';
            $ipstr2 ='';
            $ipstr3 ='';
            if(filter_var($clientip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4) !== false){
                if(empty($data['V4_IP1']) && empty($data['V4_IP2']) && empty($data['V4_IP3'])){
                    return true;
                }else{
                    if(!empty($data['V4_IP1'])){
                        $maskstr1 = $this->mask2cidr($data['V4_Mask1']);
                        $ipstr1 = $data['V4_IP1']."/".$maskstr1;
                        $ipc1 = new ipCheck($ipstr1);
                        $clientip = $ipc1->get_client_ip();
                        if($ipc1->check($clientip)){
                            $ip1 = true;
                        }
                    }
                    if(!empty($data['V4_IP2'])){
                        $maskstr2 = $this->mask2cidr($data['V4_Mask2']);
                        $ipstr2 = $data['V4_IP2']."/".$maskstr2;
                        $ipc2 = new ipCheck($ipstr2);
                        $clientip = $ipc2->get_client_ip();
                        if($ipc2->check($clientip)){
                            $ip2 = true;
                        }
                    }
                    if(!empty($data['V4_IP3'])){
                        $maskstr3 = $this->mask2cidr($data['V4_Mask3']);
                        $ipstr3 = $data['V4_IP3']."/".$maskstr3;
                        $ipc3 = new ipCheck($ipstr3);
                        $clientip = $ipc3->get_client_ip();
                        if($ipc3->check($clientip)){
                            $ip3 = true;
                        }
                    }

                }
            }
            if(filter_var($clientip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV6) !== false){
                //IPV6地址管理
                if(empty($data['V6_IP1']) && empty($data['V6_IP2']) && empty($data['V6_IP3'])){
                    return true;
                }else {
                    if(!empty($data['V6_IP1'])){
                        $clientipbin = substr($this->ip62bin($clientip),0,$data['V6_Mask1']);
                        $ip1bin = substr($this->ip62bin($data['V6_IP1']),0,$data['V6_Mask1']);
                        if($clientipbin == $ip1bin){
                            $ip1 = true;
                        }
                    }
                    if(!empty($data['V6_IP2'])){
                        $clientipbin2 = substr($this->ip62bin($data['$clientip']),0,$data['V6_Mask2']);
                        $ip2bin = substr($this->ip62bin($data['V6_IP2']),0,$data['V6_Mask2']);
                        if($clientipbin2 == $ip2bin){
                            $ip2 = true;
                        }
                    }
                    if(!empty($data['V6_IP3'])){
                        $clientipbin3 = substr($this->ip62bin($data['$clientip']),0,$data['V6_Mask3']);
                        $ip3bin = substr($this->ip62bin($data['V6_IP3']),0,$data['V6_Mask3']);
                        if($clientipbin3 == $ip3bin){
                            $ip3 = true;
                        }
                    }
                    
                }
            }
            if($ip1 || $ip2 || $ip3){
                return true;
            }else{
                return false;
            }
        }

    }

    //登录异常插入一条数据到表m_tblog_sys_resource
    private function getLoginAbnor($sMessage , $iUserId = false){
        $Alert = TbConfig::model()->find('sName=:sName', array(':sName'=>'mailAlert'));
        $Alert = json_decode($Alert['sValue'],true);
        $success = true;
        if($Alert['alert_enable'] == 'on'){

            $hModel = new TbLogSysResource();
            $hModel->iTime = time();
            $hModel->sSubject = '登录异常';
            $hModel->sContent = $sMessage;
            $iUserId && $hModel->iUserId = intval($iUserId);
            $r = $hModel->save();
        }
        if($r){
            return $success;
        }
    }



}