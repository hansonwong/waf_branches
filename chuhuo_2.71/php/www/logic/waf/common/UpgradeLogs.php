<?php

namespace app\logic\waf\common;

use Yii;
use app\models\Devinfo;

/**
 * 规则升级与系统升级
 * Class UpgradeLogs
 * @package app\logic\waf\common
 */
class UpgradeLogs extends \app\modelLogs\UpgradeLogs
{
    public $upVersion;
    public $curVersion;
    public $_sFileType;
    public $_sContent;

    /**
     * 检查版本号与入库
     * @param string $sFile
     * @return array
     */
    public function addLog($sFile)
    {
        $data = ['code'=>false, 'info'=>'', 'id'=>''];

        $sFile = strtolower(trim($sFile));
        $rst = $this->checkFile($sFile);
        if( $rst['code'] != true )
        {
            $data['info'] = $rst['info'];

            return $data;
        }

        $rst = $this->saveData($sFile);
        if( $rst===0 )
        {
            $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol('saveFailed');//"保存失败";
            return $data;
        }

        $data['code'] = true;
        $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol('success'); //'成功';
        $data['id'] = $rst;
        return $data;
    }

    private function checkFile($sFile)
    {
        $data = ['code'=>false, 'info'=>''];

        if( strpos($sFile, '.tar') === false )
        {
            $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol('upgradeFilePackageError'); //'升级文件包错误';
            return $data;
        }

        if( strpos($sFile, 'rule_v') === false && strpos($sFile, 'sys_v') === false )
        {
            $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol('upgradeFilePackageError'); //'升级文件包错误';
            return $data;
        }

        // 获取文件版本号 1.1 | 1.8e
        $this->upVersion = $this->getVersion($sFile);

        // 判断当前版本号命令是否正确
        $rst = $this->checkVersion($this->upVersion);
        if( $rst===false )
        {
            $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol('versionNumberError'); //'版本号错误';
            return $data;
        }

        // 检查之前有没有更新成功过
        $sWhere = "sFileName='{$sFile}' AND iUpdateResult=1";
        $rst = UpgradeLogs::find()->where($sWhere)->count();
        if( $rst>0 )
        {
            $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol('theVersionHasBeenUpgraded'); //'版本已升级过';
            return $data;
        }

        // 推算出上一个版本号 1.8|1.7
        $preVersion = $this->getPreVersion($this->upVersion);
        // 获取系统版本 1.1|1.8e
        $this->curVersion = $this->getCurVersion($sFile);
        if( strlen($this->curVersion)<1 )
        {
            $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol('currentVersionInformationError'); //'当前版本信息错误';
            return $data;
        }

        $rst = $this->matchingVersion($preVersion, $this->curVersion, $this->upVersion);
        if( $rst===false )
        {
            $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol('upgradeVersionError'); //'升级版本错误';
            return $data;
        }

        $data['code'] = true;
        $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol('success'); //'成功';
        return $data;
    }

    /**
     * 根据上传的文件名，取出版本号
     * @param $sFile
     * @return bool|string
     */
    private function getVersion($sFile)
    {
       return substr($sFile, strpos($sFile, '_v')+2,-4);
    }

    /**
     * 判断后一位版本号不大于12，超过12就向前进一位
     * @param string $version 1.1|2.7.1.1|1.8e|2.7.1.8e
     * @return bool
     */
    private function checkVersion($version)
    {
        $aVersion = explode(".", $version);
        $sL = $aVersion[count($aVersion)-2];
        $sR = $aVersion[count($aVersion)-1];

        if( !is_numeric($sL) ) return false;

        if( strpos($sR, 'e') === false && !is_numeric($sR) ) return false;

        if( intval($sR)>12 ) return false;

        return true;
    }

    /**
     * 根据当前版本与规则，推算出上一个版本号
     * @param $upVersion
     * @return string 1.12|
     */
    private function getPreVersion($upVersion)
    {
        $arr = explode(".", $upVersion);
        $iL = intval($arr[count($arr)-2]);
        $iR = intval($arr[count($arr)-1]);

        $rL = $iL;
        $rR = $iR-1;
        if( intval($iR)===0 )
        {
            $rR = 12;
            $rL = $iL-1;
        }

        return $rL.'.'.$rR;
    }

    /**
     * 根据当前升级的文件返回对应的版本号
     * @param string $sFile rule_v1.1.tar|sys_v2.7.1.1.tar
     * @return bool|string
     */
    private function getCurVersion($sFile)
    {
        $sTo = Yii::$app->sysLanguage->getTranslateBySymbol('to'); // 至
        $sUpgrades = Yii::$app->sysLanguage->getTranslateBySymbol('rulesVersionUpgrades'); // 规则版本升级

        $devInfo = Devinfo::find()->asArray()->one();
        if( strpos($sFile, 'rule_v') !==false )
        {
            $this->_sFileType = 1;
            $rule_ver = substr($devInfo['rule_ver'],1);
            $this->_sContent = "{$sUpgrades}:{$rule_ver}{$sTo}{up}";
            return $rule_ver;
        }

        if( strpos($sFile, 'sys_v') !==false )
        {
            $this->_sFileType = 2;
            $sys_ver = substr($devInfo['sys_ver'],1);
            $this->_sContent = "{$sUpgrades}:{$sys_ver}{$sTo}{up}";

            $sysVer = substr($devInfo['sys_ver'],1);
            if( count(explode(".", $sysVer))<=2 )
            {
                return "0.0";
            }

            $aVersion = explode(".", $sysVer);
            $sL = $aVersion[count($aVersion)-2];
            $sR = $aVersion[count($aVersion)-1];

            return $sL.'.'.$sR;
        }

        return '';
    }

    /**
     * 匹配版本是否一致
     * @param string $preVersion 推算出的版本号1.8
     * @param string $curVersion 当前系统的版本号1.8|1.8e
     * @param string $upVersion 正在上传的版本
     * @return bool
     */
    private function matchingVersion($preVersion, $curVersion, $upVersion)
    {
        if( $preVersion==$curVersion ) return true;

        $aUpVersion = explode(".", $upVersion);
        if( strpos($curVersion, 'e') !== false && $aUpVersion[count($aUpVersion)-1]=='0' ) return true;

        return false;
    }

    /**
     * 数据入库, 成功返回id，失败返回0
     * @param $sFile
     * @return int
     */
    private function saveData($sFile)
    {
        $sysLogin = Yii::$app->sysLogin;
        $user = $sysLogin->getUser();

        $this->_sContent = str_replace("{up}", $this->upVersion, $this->_sContent);

        $models = new self();
        $models->sFileName = $sFile;
        $models->sFileType = $this->_sFileType;
        $models->sVersion = $this->upVersion;
        $models->iUpdateTime = time();
        $models->sUserName = $user['name'];
        $models->sContent = $this->_sContent;

        if( $models->save() )
        {
            return $models->attributes['id'];
        }

        return 0;
    }
}