<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;
use app\logic\waf\common\UpgradeLogs;
use yii\data\Pagination;
/**
 * 系统-系统维护 - 规则升级
 * Class BaseConfigController
 * @package app\controllers
 */
class UpgradeController extends BaseController
{
    public $aIUpdateResult;

    public function init()
    {
        parent::init();

        $this->aIUpdateResult = [
            0 => Yii::$app->sysLanguage->getTranslateBySymbol('upgrades'), //'升级中',
            1 => Yii::$app->sysLanguage->getTranslateBySymbol('upgradeSuccess'),//'升级成功',
            -1 => Yii::$app->sysLanguage->getTranslateBySymbol('upgradeFailed') //'升级失败'
        ];
    }

    /**
     * @return array|string
     * @throws \yii\base\ExitException
     */
    public function actionConfig()
    {
        // 返回头部数据
        if( Yii::$app->request->get('op')=='header' ) return $this->GridHeader();

        // 返回表格数据
        if( Yii::$app->request->get('op')=='body' ) return $this->GridBody();

        // 检查python升级包状态
        if( Yii::$app->request->get('op')=='check' ) return $this->checkStatus();

        //判断是不是Ajax提交
        if( Yii::$app->request->isAjax )
        {
            $data = ['code' => 'F', 'info'=>'', 'id'=>0 ];
            Yii::$app->response->format = 'json';

            $downloadPath = Yii::$app->sysPath->downloadPath;
            $realPath = $downloadPath['realPath'];//用于保存到本地

            //如：/var/wafDownload/web/cache/patch12.tar
            $fileName = $_FILES['file']['name']; // 使用回上传的文件
            $sFile = $realPath.$fileName;
            if( strpos($sFile, 'rule_v') === false )
            {
                $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol('upgradeFilePackageError');//'升级文件包错误';
                return $data;
            }

            $UpgradeLogs = new UpgradeLogs();
            $rst = $UpgradeLogs->addLog($fileName);
            if( $rst['code'] != true )
            {
                $data['info'] = $rst['info'];
                Yii::$app->response->data = $data;
                Yii::$app->end();
            }
            $data['id'] = $rst['id'];

            // 上传文件处理
            $rst =Yii::$app->wafHelper->upFile($sFile, ['tar'], 100);
            if( $rst['code'] != 'T' )
            {
                $data['info'] = $rst['info'];
                Yii::$app->response->data = $data;
                Yii::$app->end();
            }

            $pcmd = "CMD_UPDATERULE|{$sFile}";
            Yii::$app->wafHelper->pipe($pcmd);

            $data['code'] = 'T';
            $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol('upgradeSuccess');
            Yii::$app->response->data = $data;
            Yii::$app->end();
        }
        else
        {
            return $this->render('index',[]);
        }
    }

    /**
     * @throws \yii\base\ExitException
     */
    private function checkStatus()
    {
        $data = ['code' => 'F', 'info'=>'', 'iUpdateResult'=>0 ];
        Yii::$app->response->format = 'json';

        $id = Yii::$app->request->post('id');
        if( intval($id)<1 )
        {
            $data['info'] = Yii::$app->sysLanguage->getTranslateBySymbol('parameterError'); //'参数错误';
            Yii::$app->response->data = $data;
            Yii::$app->end();
        }

        $models = UpgradeLogs::findOne($id);

        $data['code'] = 'T';
        $data['info'] = $this->aIUpdateResult[$models->iUpdateResult];
        $data['iUpdateResult'] = $models->iUpdateResult;
        Yii::$app->response->data = $data;
        Yii::$app->end();
    }

    /**
     * @return string
     */
    private function GridHeader()
    {
        $title = [
            ["sTitle"=> Yii::$app->sysLanguage->getTranslateBySymbol('fileName'), "data"=> "sFileName"],  //文件名
            ["sTitle"=> Yii::$app->sysLanguage->getTranslateBySymbol('versionNumber'), "data"=> "sVersion"],  //版本号
            ["sTitle"=> Yii::$app->sysLanguage->getTranslateBySymbol('time'), "data"=> "sUpdateTime"],  //时间
            ["sTitle"=> Yii::$app->sysLanguage->getTranslateBySymbol('operator'), "data"=> "sUserName"],  //操作者
            ["sTitle"=> Yii::$app->sysLanguage->getTranslateBySymbol('explain'), "data"=> "sContent"],  //说明
            ["sTitle"=> Yii::$app->sysLanguage->getTranslateBySymbol('status'), "data"=> "sUpdateResult"],  //状态
        ];
        return json_encode($title);
    }

    /**
     * @return string
     */
    private function GridBody()
    {
        // 排序
        $sortName = Yii::$app->request->post('sortname','id');
        $sortOrder = Yii::$app->request->post('sortorder','DESC');
        $orderBy = "{$sortName} {$sortOrder}";
        if( strlen($orderBy)<1 )
        {
            $orderBy = "id DESC";
        }

        $page = intval(Yii::$app->request->post('page',0));
        $page = $page>0?$page-1:$page;
        $pageSize = intval(Yii::$app->request->post('pagesize',20));

        $pagination = new Pagination(['totalCount' => UpgradeLogs::find()->count()]);
        $pagination->page = $page;
        $pagination->pageSize = $pageSize;

        $model =  UpgradeLogs::find()->orderBy($orderBy)->offset($pagination->offset)->limit($pagination->limit)->asArray()->all();
        foreach ($model as $k=>$v)
        {
            $v['sUpdateTime'] = date('Y-m-d H:i:s', $v['iUpdateTime']);
            $v['sUpdateResult'] = $this->aIUpdateResult[$v['iUpdateResult']];

            $model[$k] = $v;
        }

        $data = [
            'data'=> $model,
            'total'=> $pagination->totalCount,
            'page'=> $pagination->offset+1,
            'pagesize'=> $pageSize,
        ];
        return json_encode($data);
    }
}

