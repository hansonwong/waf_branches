<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;
use app\widget\AdminListConfig;
use app\logic\waf\common\Migrate;

/**
 * 系统 - 系统维护 - 系统升级
 * Class SysUpController
 * @package app\controllers
 */
class SysUpController extends BaseController
{
    /**
     * @param int $id
     * @return array|mixed|string
     * @throws \yii\base\ExitException
     * @throws \yii\db\Exception
     */
	public function actionConfig($id=0)
	{

        //判断是不是Ajax提交
        if( Yii::$app->request->isPost )
        {
            // 返回头部数据
            if( Yii::$app->request->get('op')=='header' ) return Migrate::getUpdateHeaderTitle();

            // 返回表格数据
            if( Yii::$app->request->get('op')=='body' ) return Migrate::getUpdateLog();

            // 升级
            if( Yii::$app->request->get('op')=='up' ) return Migrate::UpdateSys();

            // 升级 更新的操作
            if( Yii::$app->request->get('op')=='executeUpdate' ) return Migrate::executeUpdate();

            // 获取系统升级时,升级的进度
            if( Yii::$app->request->get('op')=='getUpdateSysStatus' ) return Migrate::getUpdateSysStatus();

            // 还原
            if( Yii::$app->request->get('op')=='returnSystem' ) return Migrate::returnSystem();

            // 还原 更新的操作
            if( Yii::$app->request->get('op')=='executeReturn' ) return Migrate::executeReturn();

            // 还原 更新的操作
            if( Yii::$app->request->get('op')=='getReturnSysStatus' ) return Migrate::getReturnSysStatus();

            // 查询是否重启系统
            if( Yii::$app->request->get('op')=='restartSystem' ) return Migrate::restartSystem();

            //$info = $this->translate->getTranslateBySymbol('modifySuccess');
            //AdminListConfig::returnSuccessFieldJson('T',$info,true);
        }
        else
        {
            //升级 进度条
            if( Yii::$app->request->get('op')=='Loading' ) return Migrate::Loading($this);

            //还原 进度条
            if( Yii::$app->request->get('op')=='returnLoading' ) return Migrate::returnLoading($this);

            //检测系统是否已重启完
            if( Yii::$app->request->get('op')=='sysStatus' ) return $this->getSysStatus();

            return $this->render('index',[]);
        }
	}

    /**
     * @throws \yii\base\ExitException
     */
	private function getSysStatus()
    {
        $aData['code'] = 'T';
        $aData['info'] = 'success';
        echo json_encode($aData);

        Yii::$app->end();
    }
}
