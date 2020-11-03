<?php
namespace app\logic\sys;

use Yii;

/**
 * 系统全局目录类
 * Class SysPath
 * @package app\logic\sys
 */

class SysPath {
    public
        $projectRootPath,//项目根目录路径
        $resourcePath,//请求静态资源路径
        $actionPath,
        $routePass,//免权限检测路由路径
        $routePassController,//免权限检测路由控制器
        $routePassForLoginTimeout,//访问路由不刷新登录超时
        $cachePath,//web缓存路径
        $downloadPath,//web缓存下载路径
        $wafReportPath,//WAF日志下载路径
        $loopholeScanResultPath,//漏洞扫描文件存放路径
        $systemUpgradePath,#系统升级迁移目录
        $systemDebugPath;//系统调试文件输出路径

    public function __construct()
    {
        $sysParams = Yii::$app->sysParams;
        $this->projectRootPath = $sysParams->getParamsChild(['systemPath', 'projectRootPath']);
        $this->resourcePath = $sysParams->getParamsChild(['systemUrl', 'prefix', 'waf']);
        $this->actionPath = '';
        $this->routePass = $sysParams->getParamsChild(['systemUrl', 'routePass', 'route']);
        $this->routePassController = $sysParams->getParamsChild(['systemUrl', 'routePass', 'controller']);
        $this->routePassForLoginTimeout = $sysParams->getParamsChild(['systemUrl', 'routePassForLoginTimeout']);
        $this->cachePath = $sysParams->getParamsChild(['systemPath', 'cachePath']);
        $this->downloadPath = $sysParams->getParamsChild(['systemPath', 'downloadPath']);
        $this->wafReportPath = $sysParams->getParamsChild(['systemPath', 'wafReportPath']);
        $this->loopholeScanResultPath = $sysParams->getParamsChild(['systemPath', 'loopholeScanResultPath']);
        $this->systemUpgradePath = $sysParams->getParamsChild(['systemPath', 'systemUpgradePath']);
        $this->systemDebugPath = $sysParams->getParamsChild(['systemPath', 'debugLog']);
    }
}