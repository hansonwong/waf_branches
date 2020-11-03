<?php

namespace app\models;

use Yii;
use app\logic\model\BaseModel;
use app\widget\AdminListConfig;
/**
 * This is the model class for table "t_scantask".
 *
 * @property integer $id
 * @property string $name
 * @property string $url
 * @property integer $starttime
 * @property integer $endtime
 * @property integer $status 0=>'未扫描', 1=>'扫描中', 2=>'已完成', 3=>'已停止', 4=>'扫描失败'
 * @property string $result
 */
class ScanTask extends BaseModel
{
    public static function tableName()
    {
        return 't_scantask';
    }

    public function rulesSource()
    {
        return [
            [['starttime', 'endtime', 'status'], 'integer'],
            [['name', 'url', 'result'], 'string', 'max' => 255],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'name' => '任务名称',
            'url' => '扫描地址',
            'starttime' => '开始时间',
            'endtime' => '完成时间',
            'status' => '扫描状态',
            'result' => '扫描结果',
        ];
    }

    public function beforeSave($insert)
    {
        $ScanTaskModel = self::find()->where(['status'=>1])->count();
        if( $ScanTaskModel>0 )
        {
            $info = $this->translate->getTranslateBySymbol('existingTasksAreInProgress').',';  //已有任务正在进行中,
            $info .= $this->translate->getTranslateBySymbol('waitForTheTaskToFinishAndAddNewTasks');  //,请等待任务完成再添加新任务
            Yii::$app->sysJsonMsg->msg('F', $info);
        }
        return parent::beforeSave($insert);
    }

    // 检测有没有正在扫描的
    public static function checkBeforeDelete($idArr){
        $count = self::find()->where(['status' => 1, id => $idArr])->count();
        if(0 < $count) {
            Yii::$app->sysJsonMsg->msg(false, Yii::$app->sysLanguage->getTranslateBySymbol('stopTaskBeforeDeleting'));
        }
    }

    public function afterDelete()
    {
        $realPath = (Yii::$app->sysPath->loopholeScanResultPath)['realPath'];//用于保存到本地
        $id = $this->id;
        $file = "{$realPath}{$id}";
        $file_zip = "{$file}.zip";
        @unlink($file);
        @unlink($file_zip);

        Yii::$app->wafHelper->pipe("CMD_SITESCAN|{$id}|0");
        parent::afterDelete();
    }

    public function ListSearch()
    {
        return [
            'field' => [],
            'key' => $this->modelName,
            'model' => $this,
        ];
    }

    public function ListTable()
    {
        return [
            'field' => [
                'name', 'url',
                'starttime' => ['type' => 'custom', 'valType' => 'datetime'],
                'endtime' => ['type' => 'custom', 'valType' => 'datetime'],
                'status' => ['type' => 'callback', 'val' => function($obj, $val){
                    $list = [
                        0 => 'notScanning',
                        1 => 'scanningAlready',
                        2 => 'completed',
                        3 => 'stopped',
                        4 => 'scanFailure',
                    ];
                    return Yii::$app->sysLanguage->getTranslateBySymbol($list[$val]);
                }],
            ],
            'recordOperation' => [
                'delete' => false, 'update' => false,
                [
                    'title' => Yii::$app->sysLanguage->getTranslateBySymbol('startUp'),#开始
                    'url' => 'javascript:scanStartAndStop(1, %s);',
                    'class' => 'bt_qidong list-btn',
                    #跳过权限判断
                    'authorityPass' => true,
                    #是否显示
                    'returnAllow' => function($data){
                        return in_array($data->status, [null, 0, 3, 4]);
                    },
                ],
                [
                    'title' => Yii::$app->sysLanguage->getTranslateBySymbol('stopIt'),#停止
                    'url' => 'javascript:scanStartAndStop(3, %s);',
                    'class' => 'bt_stop list-btn',
                    'authorityPass' => true,
                    'returnAllow' => function($data){
                        return in_array($data->status, [1]);
                    },
                ],
                [
                    'title' => Yii::$app->sysLanguage->getTranslateBySymbol('scanning'),#扫描
                    'url' => 'javascript:scanStartAndStop(1, %s);',
                    'class' => 'bt_scan list-btn',
                    'authorityPass' => true,
                    'returnAllow' => function($data){
                        return in_array($data->status, [2]);
                    },
                ],
                'view' => [
                    'title' => Yii::$app->sysLanguage->getTranslateBySymbol('see'),#查看
                    'url' => function($data){
                        $frameSize = Yii::$app->sysParams->getParams('hui-frame-size');
                        $viewButtonText = Yii::$app->sysLanguage->getTranslateBySymbol('see');

                        $id = $data->id;
                        $downloadPath = Yii::$app->sysPath->loopholeScanResultPath;
                        $realPath = $downloadPath['realPath'];//用于保存到本地
                        $downPath = $downloadPath['downPath'];//用于下载

                        $file = "{$realPath}{$id}/index.html";
                        if(!file_exists($file))
                            return "javascript:$.Layer.alert({msg: top.translation.t(\"theScanDoesNotExist\") + \",\" + top.translation.t(\"reScanning\") + \"!\",});";

                        $url = "{$downPath}{$id}/index.html";
                        return "javascript:dataBox(\"{$viewButtonText}\", \"{$url}\", \"{$frameSize['width']}\", \"{$frameSize['height']}\");";
                    },
                    'class' => 'bt_view list-btn',
                    'returnAllow' => function($data){
                        return in_array($data->status, [2]);
                    },
                ],
                [
                    'title' => Yii::$app->sysLanguage->getTranslateBySymbol('download'),#下载
                    'url' => function($data){
                        $id = $data->id;
                        $downloadPath = Yii::$app->sysPath->loopholeScanResultPath;
                        $realPath = $downloadPath['realPath'];//用于保存到本地
                        $downPath = $downloadPath['downPath'];//用于下载

                        $file = "{$realPath}{$id}.zip";
                        if(!file_exists($file))
                            return "javascript:$.Layer.alert({msg: top.translation.t(\"theScanDoesNotExist\") + \",\" + top.translation.t(\"reScanning\") + \"!\",});";

                        return "{$downPath}{$id}.zip";
                    },
                    'class' => 'bt_download list-btn',
                    'authorityPass' => true,
                    'returnAllow' => function($data){
                        return in_array($data->status, [2]);
                    },
                ],
            ],
            'model' => $this,
            'customStr' => \Yii::$app->view->renderFile('@app/views/vulnerability-scan/list-component.php'),
        ];
    }

    public function ListField()
    {
        $type = AdminListConfig::ListFieldScenarios('common', $this);
        $fieldKey = $this->modelName;

        $fieldType = [
            'id' => ['showType' => 'hidden'],
            'starttime' => ['showType' => 'hidden'],
            'endtime' => ['showType' => 'hidden'],
            'status' => ['showType' => 'hidden'],
            'result' => ['showType' => 'hidden'],
            'url' => [
                'tips' => Yii::$app->sysLanguage->getTranslateBySymbol('as').': http://www.example.com',
                'tipsPs' => Yii::$app->sysLanguage->getTranslateBySymbol('fillInTheRealAndValidScanningAddress').','.Yii::$app->sysLanguage->getTranslateBySymbol('otherwiseItCanNotBeScanned'),
            ],
        ];
        switch ($type) {
            case 'create' :
                break;
            case 'update' :
                $fieldType['name']['showType'] = 'show';
                break;
            default :
                ;
        }
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => $fieldType,
            'customStr' => false,
        ];
        return $field;
    }

    /**
     * 扫描开始/停止
     * @param $status 状态 1:扫描 3:停止
     * @param $id
     */
    public static function scanStartAndStop($status, $id){
        $model = self::findOne($id);
        $model->status = $status;

        if(1 == $status){
            $model->starttime = time();
            $model->endtime = '';
        }

        if(!$model->save()) Yii::$app->sysJsonMsg->msg(true, '');

        Yii::$app->wafHelper->pipe("CMD_SITESCAN|{$id}|{$status}");
        Yii::$app->sysJsonMsg->msg(true, '');
    }
}
