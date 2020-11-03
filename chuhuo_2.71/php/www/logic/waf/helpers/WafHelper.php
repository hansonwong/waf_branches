<?php

namespace app\logic\waf\helpers;

use Yii;
use yii\helpers\Html;
use app\logic\waf\helpers\WafRegexp;
class WafHelper
{
    /**
     * $fifofile = '/Data/apps/wwwroot/firewall/fifo/second_firewall.fifo';
     * 写入命名管道
     * @param $msg
     * @return bool
     */
    public static function pipe($msg)
    {
        $fp = @fopen("/tmp/bdwaf.fifo", 'w+r+b');
        if( $fp === FALSE )
        {
            return FALSE;
        }

        if( !@fwrite($fp,$msg."\n") )//写
        {
            return FALSE;
        }
        if( !@fclose($fp) )
        {
            return false;
        }

        return true;
    }

    /**
     * 防火墙管道
     * 保存命令标识符到管道文件
     * @param null $sCommand
     * @param string $sFileName
     * @return bool
     */
    public static function firePipe($sCommand = null,$sFileName='')
    {

        $sCommand = trim($sCommand);
        if( strlen($sCommand)<1 ) return FALSE;

        $fifoFile = '/Data/apps/wwwroot/firewall/fifo/second_firewall.fifo';
        $sFile =$sFileName?$sFileName:$fifoFile;

        $fp = @fopen($sFile, 'w+r+b');
        if( $fp === FALSE )
        {
            return FALSE;
        }

        if( !@fwrite($fp,$sCommand."\n") )//写
        {
            return FALSE;
        }
        if( !@fclose($fp) )
        {
            return false;
        }

        return true;
    }

    /**
     * 端口信息写入文件
     * @param string $content 写入的文件内容
     * @param string $file
     * @return bool
     */
    public static function writeFile($content, $file="")
    {
        if( strlen($file)<1 )
        {
            $file = Yii::$app->sysPath->cachePath."waf_port.conf";
        }

        $fp = @fopen($file, "w");
        if( $fp === FALSE )
        {
            return FALSE;
        }
        if( !@fwrite($fp, $content) )
        {
            return FALSE;
        }
        if( !@fclose($fp) )
        {
            return FALSE;
        }

        return TRUE;
    }

    /**
     * 上传单个文件到指定目录
     * @param $sFile string 上传文件的路径与文件名
     * @param $extensionArr array 限制上传的扩展名 ['dat']
     * @param $fileSize integer 限制上传的文件大小 默认不大于3M
     * @param bool $isExtIn 限制上传的扩展名，是包含还是不包含
     * @return array
     */
    public static function upFile($sFile, $extensionArr=[], $fileSize=3, $isExtIn=false)
    {
        $data = ['code'=>'F', 'info'=>''];

        if( strlen($sFile)<1 )
        {
            $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol('validationFileAvailable');
            return $data;
        }

        if( strlen($_FILES["file"]["tmp_name"])<1 )
        {
            $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol('unabletoObtainUploadFileInformation').",".Yii::$app->sysLanguage->getTranslateBySymbol('validationFileAvailable')."?";
            return $data;
        }

        if ( $_FILES["file"]["error"] > 2 )
        {
            $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol('fileUploadFailed');
            return $data;
        }

        $fileSize = intval($fileSize);
        if( intval($_FILES["file"]["size"] / 1048576) > $fileSize )
        {
            $data['info'] = str_replace("%s", $fileSize, Yii::$app->sysLanguage->getTranslateBySymbol("Don'tUploadFilesLargerThan%sM"));
            return $data;
        }

        // 提取上传文件扩展名
        if( !empty($extensionArr) )
        {
            $fileArr = pathinfo($_FILES['file']['name']);
            if( $isExtIn===false )
            {
                if( !in_array($fileArr['extension'], $extensionArr) )
                {
                    // '只允许上传限制的扩展名上传格式的文件!';
                    $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol("uploadOnlyAllowed");
                    $data['info'] .= implode(",", $extensionArr);
                    $data['info'] .= Yii::$app->sysLanguage->getTranslateBySymbol("formattedFile");
                    return $data;
                }
            }

            if( $isExtIn===true )
            {
                if( in_array($fileArr['extension'], $extensionArr) )
                {
                    // '不允许上传限制的扩展名上传格式的文件!';
                    $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol("canNotAllowUpload");
                    $data['info'] .= implode(",", $extensionArr);
                    $data['info'] .= Yii::$app->sysLanguage->getTranslateBySymbol("formattedFile");
                    return $data;
                }
            }

        }

        if( move_uploaded_file($_FILES["file"]["tmp_name"], $sFile) ===FALSE )
        {
            $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol('fileUploadFailed');
            return $data;
        }

        $data['code'] = 'T';
        $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol('uploadSuccessfully');

        return $data;
    }

    /**
     * 验证数据，根据model检验，返回出错信息
     * @param $model
     * @return string
     */
    public static function getModelErrors($model)
    {
        $info = '未知错误';
        $errors = $model->getErrors();
        foreach( $model->activeAttributes() as $ati )
        {
            if( isset( $errors[$ati] ) && !empty( $errors[$ati] ) )
            {
                $info = $errors[$ati][0];
            }
        }

        return $info;
    }

    /**
     * IP十进制表示
     * @param $ip
     * @return int
     */
    public static function getDecIp($ip)
    {
        $ip = explode(".", $ip);
        return $ip[0]*255*255*255+$ip[1]*255*255+$ip[2]*255+$ip[3];
    }

    /**
     * 检查ipv6地址，1代表只检查IPV6地址，2代表检查“ipv6/64”这种格式
     * @param $ipv
     * @param int $type
     * @return bool
     */
    public static function CheckIPV6($ipv,$type=1)
    {
        if($type ==1){
            $res = preg_match(WafRegexp::$ip6,$ipv);
            if($res){
                return true;
            }else{
                return false;
            }
        }
        if($type ==2)
        {
            $iparr = explode("/",$ipv);
            $ipcount= count($iparr);
            if($ipcount ==2 && strlen($iparr[1])>0)
            {
                $res = preg_match(WafRegexp::$ip6,$iparr[0]);
                if(!$res){
                    return false;
                }else{
                    if($iparr[1]<0 || $iparr[1]>128){
                        return false;
                    }
                }
                return true;
            }else{
                return false;
            }
        }
    }

    /**
     * 检查是否是正确的IPV4地址
     * @param $ipaddress
     * @param int $type
     * @return bool
     */
    public static function CheckIPV4($ipaddress,$type=1)
    {
        //$type等于1的时候是ip地址，等于2的时候是ip地址加掩码位数  等于3的时候验证ip地址(PHP自带函数)
        if($type==1){
            if(filter_var($ipaddress,FILTER_VALIDATE_IP,FILTER_FLAG_IPV4)){
                return true;
            }else{
                return false;
            }
        }elseif($type==2){
            if(preg_match(WafRegexp::$ospf_preg,$ipaddress)){
                return true;
            }else{
                return false;
            }
        }elseif($type==3){
            $ipaddressarr = explode(".",$ipaddress);
            $count = count($ipaddressarr);
            if($count ==4){
                if(is_numeric($ipaddressarr[0])&&is_numeric($ipaddressarr[1])&&is_numeric($ipaddressarr[2])&&is_numeric($ipaddressarr[3])&&$ipaddressarr[0]>=0&&$ipaddressarr[0]<=255&&$ipaddressarr[1]>=0&&$ipaddressarr[1]<=255&&$ipaddressarr[2]>=0&&$ipaddressarr[2]<=255&&$ipaddressarr[3]>=0&&$ipaddressarr[3]<=255){
                    return true;
                }else{
                    return false;
                }
            }else{
                return false;
            }
        }
    }

    /**
     * 判断2个网段是否属于有同网段，或者说2个网段之间是否有交集
     * @param $ip 192.168.15.1/30 OR 192.168.15.1/255.255.255.252
     * @param $ip2 192.168.15.10/30  OR 192.168.15.10/255.255.255.252
     * @return bool false
     */
    public static function isNetSome($ip, $ip2)
    {
        list($ip, $CIDR1) = explode('/', $ip);
        list($ip2, $CIDR2) = explode('/', $ip2);
        if (strpos($CIDR1, '.') !== false) {
            $CIDR1 = self::mask2cidr2($CIDR1);
        }
        if (strpos($CIDR2, '.') !== false) {
            $CIDR2 = self::mask2cidr2($CIDR2);
        }

        if ($CIDR1 != $CIDR2) {
            return false;
        } else {
            $ip = self::ip2Bin2($ip);
            $ip2 = self::ip2Bin2($ip2);

            return substr($ip, 0, $CIDR1) == substr($ip2, 0, $CIDR2);
        }
    }

    public static function mask2cidr2($mask)
    {
        $long = ip2long($mask);
        $base = ip2long('255.255.255.255');
        return 32 - log(($long ^ $base) + 1, 2);
    }

    public static function ip2Bin2($ip)
    {
        $ips = explode(".", $ip);
        $ipbin = "";
        foreach ($ips as $iptmp) {
            $ipbin .= sprintf("%08b", $iptmp);
        }
        return $ipbin;
    }

    /**
     * /数据转换成json格式
     * @param $data
     * @return mixed
     */
    public static function fireConvertData($data)
    {
        foreach ($data as $k => $v)
        {
            $isJson = json_decode($v);
            if ($isJson)
            {
                $data[$k] = json_decode($v);
            }
            else
            {
                $data[$k] = "$v";
            }
        }
        return str_ireplace("\\\"", "\"", json_encode($data));
    }

    /**
     * 创建 指定 目录
     * @param $directoryArr
     * @param int $mode 默认0755
     * @return bool
     */
    public static function mkDir($directoryArr, $mode=0755)
    {
        if( empty($directoryArr) ) return false;

        foreach( $directoryArr as $v )
        {
            if ( is_dir($v) === TRUE ) continue;

            if( mkdir($v, $mode, true) === FALSE )
            {
                return false;
            }
        }

        return true;
    }

    /**
     * 应急支持
     */
    public static function sos(){
        Yii::$app->wafHelper->pipe('CMD_TAR_SYSTEMINFO_SEND');
        Yii::$app->sysJsonMsg->msg(true, Yii::$app->sysLanguage->getTranslateBySymbol('technicalSupportCmdAlreadySend'));
    }

    /**
     * 获取post与get数据
     * @return object 返回对象
     */
    public static function getParam()
    {
        if( Yii::$app->request->isPost )
        {
            if( !empty($_GET) )
            {
                $_POST = array_merge($_POST, $_GET);
            }

            foreach ($_POST as $k => $v)
            {
                if ( !is_array($v) )
                {
                    $_POST[$k] = Html::encode($v);
                    continue;
                }

                foreach ($v as $key => $value)
                {
                    $_POST[$k][$key] = Html::encode($value);
                }
            }

            return (object)$_POST;
        }

        foreach ($_GET as $k => $v)
        {
            if( !is_array($v) )
            {
                $_GET[$k] = Html::encode($v);
                continue;
            }

            foreach ($v as $key => $value)
            {
                $_POST[$k][$key] = Html::encode($value);
            }
        }
        return (object)$_GET;
    }

    /**
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
}