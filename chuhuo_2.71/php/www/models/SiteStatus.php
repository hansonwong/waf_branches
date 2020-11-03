<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;
use app\logic\model\tools\SelectList;
/**
 * This is the model class for table "t_sitestatus".
 *
 * @property integer $id
 * @property string $url
 * @property integer $time
 * @property integer $status
 * @property integer $result
 * @property string $desc
 * @property string $protype
 * @property integer $freq
 * @property double $responsetime
 * @property integer $type
 * @property integer $rate
 */
class SiteStatus extends BaseModel
{
    public static function tableName()
    {
        return 't_sitestatus';
    }

    public function rulesSource()
    {
        return [
            [['time', 'status', 'result', 'freq', 'type', 'rate'], 'integer'],
            [['responsetime'], 'number'],
            [['url'], 'string', 'max' => 1024],
            [['desc', 'protype'], 'string', 'max' => 512],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'url' => '监控目标URL',
            'time' => '最近执行时间',
            'status' => '是否启用',
            'result' => '状态',
            'desc' => 'Desc',
            'protype' => 'Protype',
            'freq' => 'Freq',
            'responsetime' => '响应时间',
            'type' => 'Type',
            'rate' => '监控频率',
        ];
    }

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => ['status',],
            '~' => ['url',],
        ]);
        return ['query' => $query];
    }

    public function returnTimeLabel(){
        $timeArr = [5, 10, 30, 60, 120, 240, 480, 720];
        $timeLabel = [];
        foreach ($timeArr as $val){
            $timeLabel[$val] = ($val >= 60) ?
                ($val/60).Yii::$app->sysLanguage->getTranslateBySymbol('hour') ://小时
                $val.Yii::$app->sysLanguage->getTranslateBySymbol('minute');//分钟
        }
        return $timeLabel;
    }

    /**
     * 搜索配置
     * @return array
     */
    public function ListSearch()
    {
        return [
            'field' => [
                'url',
                'status' => SelectList::enable('select'),
            ],
            'key' => $this->modelName,
            'model' => $this,
        ];
    }

    public function ListTable()
    {
        $enable = Yii::$app->sysLanguage->getTranslateBySymbol('enable');
        $stopUse = Yii::$app->sysLanguage->getTranslateBySymbol('stopUse');

        return [
            'publicButton' => [
                ['button' => "<input type=button class='btn c_b btn_open' value='{$enable}' onclick='statusChange(0, 1);'>", 'authorityPass' => true],
                ['button' => "<input type=button class='btn c_o btn_stop' value='{$stopUse}' onclick='statusChange(0, 0);'>", 'authorityPass' => true],
            ],
            'field' => [
                'url',
                'rate' => ['type' => 'switch', 'val' => AdminListConfig::returnSelect('switch', $this->returnTimeLabel())],
                'time' => ['type' => 'custom', 'valType' => 'datetime'],
                'responsetime' => ['type' => 'callback', 'val' => function($obj, $val){
                    return sprintf("%.2f", $val).Yii::$app->sysLanguage->getTranslateBySymbol('second');
                }],
                'result' => ['type' => 'callback', 'val' => function($obj, $val){
                    $str = ( $val == 0) ? 'stopUse' : 'normal';
                    return Yii::$app->sysLanguage->getTranslateBySymbol($str);
                }],
                'status' => ['type' => 'callback', 'val' => function($obj, $val){
                    $class = (1 == $val) ? 'bt_qyan' : 'bt_tyan';
                    $str =  (1 == $val) ? 'enable' : 'stopUse';
                    $status = 1 == $val ? 0 : 1;
                    $str = Yii::$app->sysLanguage->getTranslateBySymbol($str);
                    return "<input type=button class='qt {$class}' onclick='statusChange({$obj['id']}, {$status});' title='{$str}'>";
                }],
            ],
            'model' => $this,
            'customStr' => \Yii::$app->view->renderFile('@app/views/rule-custom-defend-policy/list-component.php').
                \Yii::$app->view->renderFile('@app/views/site-status/html.php'),
        ];
    }

    /**
     * 字段修改、添加配置
     * @return array
     */
    public function ListField()
    {
        $type = AdminListConfig::ListFieldScenarios('common', $this);
        $fieldKey = $this->modelName;

        $fieldType = [
            'id' => ['showType' => 'hidden'],
            'time' => ['showType' => 'hidden'],
            'status' => ['showType' => 'hidden'],
            'result' => ['showType' => 'hidden'],
            'desc' => ['showType' => 'hidden'],
            'protype' => ['showType' => 'hidden'],
            'freq' => ['showType' => 'hidden'],
            'responsetime' => ['showType' => 'hidden'],
            'type' => ['showType' => 'hidden'],
            'url' => ['tipsPsTKey' => ['fillInTheRealAndValidMonitoringAddress']],
            'rate' => AdminListConfig::returnSelect('select', $this->returnTimeLabel()),
        ];
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => $fieldType,
        ];
        switch ($type) {
            case 'create' :
                break;
            case 'update' :
                break;
            default :
                ;
        }
        return $field;
    }

    public static function updateStatus(){
        $model = new self;
        $query = Yii::$app->request->bodyParams;
        $id = $query['id'];
        $status = $query['status'];
        if(!is_array($id)) return false;
        foreach ($id as $item) {
            if ('' != $item) {
                $obj = $model->findOne($item);
                #$obj->sendPipe = false;
                $obj->status = $status;
                $obj->save(false);
            }
        }
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        Yii::$app->sysJsonMsg->msg(true, '', false);
    }

    public static function getDetail(){
        $id = Yii::$app->request->post('id');
        $model =  self::find()->where(['id'=>$id])->asArray()->one();
        return json_encode($model);
    }

    public static function getViewData($id){
        $translate = Yii::$app->sysLanguage;
        $model = self::findOne($id);

        $select = "new_table_name";
        $s_time = strtotime(Yii::$app->request->post('startDate','0'));
        $e_time = strtotime(Yii::$app->request->post('endDate','0'));

        $whereStr = "ori_table_name='t_sitestatus' and start_time <= {$e_time} and end_time >= {$s_time}";
        $tabNames =  RecordHistory::find()->select($select)->where($whereStr)->asArray()->all();
        if( empty($tabNames) )
        {
            $info = $translate->getTranslateBySymbol('noData'); //无数据
            AdminListConfig::returnSuccessFieldJson('F', $info, true);
        }

        $tables = [];
        foreach($tabNames as $v)
        {
            array_push($tables,'logs.'.$v['new_table_name']);
        }

        // logs.t_sitestatus_20171205,logs.t_sitestatus_20171201,logs.t_sitestatus_20171202,logs.t_sitestatus_20171203,logs.t_sitestatus_20171204
        $tables = implode(',',$tables);

        // 删除 t_sitestatus_all数据表
        $sqlstr = "drop table if exists t_sitestatus_all";
        $rc = Yii::$app->db->createCommand($sqlstr)->execute();
        if($rc != 0)
        {
            $info = $translate->getTranslateBySymbol('systemError'); //系统错误
            AdminListConfig::returnSuccessFieldJson('F', $info, true);
        }

        // 创建一个表
        $sqlstr = "create table `t_sitestatus_all` (
            `id` int(11) NOT NULL AUTO_INCREMENT,
            `url` varchar(1024) COLLATE utf8_unicode_ci DEFAULT NULL,
            `time` int(11) DEFAULT NULL,
            `status` tinyint(4) DEFAULT '0' COMMENT '0:disable 1:enable',
            `result` tinyint(4) DEFAULT '0' COMMENT '0:unnormal 1:normal',
            `desc` varchar(512) COLLATE utf8_unicode_ci DEFAULT '',
            `protype` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
            `freq` int(11) DEFAULT NULL,
            `responsetime` float DEFAULT NULL,
            `type` tinyint(4) DEFAULT '0',
            `rate` int(10) DEFAULT NULL,
             PRIMARY KEY (`id`)
            ) ENGINE=MRG_MYISAM UNION=($tables) INSERT_METHOD=LAST DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;";
        $rc = Yii::$app->db->createCommand($sqlstr)->execute();
        if($rc != 0)
        {
            $info = $translate->getTranslateBySymbol('systemError'); //系统错误
            AdminListConfig::returnSuccessFieldJson('F', $info, true);
        }

        $select = "responsetime,time,result";
        $whereStr = "url='{$model['url']}' and time >= {$s_time} and time <= {$e_time}";

        $query = new yii\db\Query();
        $query->select($select)->from('t_sitestatus_all')->where($whereStr)->orderBy('time');

        //时间分布变量
        $sum_0ms=$sum_100ms=$sum_500ms=$sum_1s=$sum_10s=$sum_30s=$sum_60s=$sum_180s=$sum_300s=0;
        $arrRt = [];//响应时间数组
        $arrNormal = [];//正常数据数组
        foreach($query->each() as $v)
        {
            $v['responsetime'] = $v['responsetime'] *1000;
            $itemTime = date('m-d H:i:s',$v['time']);

            //响应时间
            $arrRt[$itemTime] = $v['responsetime'];

            //异常数据
            $arrNormal[$itemTime] = 0;
            //正常数据
            if($v['result']==1)
            {
                $arrNormal[$itemTime] =1;
            }

            $sum_0ms += ($v['responsetime'] > 0 && $v['responsetime'] <= 100)?1:0;
            $sum_100ms += ($v['responsetime'] > 100 && $v['responsetime'] <= 500)?1:0;
            $sum_500ms += ($v['responsetime'] > 500 && $v['responsetime'] <= 1000)?1:0;
            $sum_1s += ($v['responsetime'] > 1000 && $v['responsetime'] <= 1000*10)?1:0;
            $sum_10s += ($v['responsetime'] > 1000*10 && $v['responsetime'] <= 1000*30)?1:0;
            $sum_30s += ($v['responsetime'] > 1000*30 && $v['responsetime'] <= 1000*60)?1:0;
            $sum_60s += ($v['responsetime'] > 1000*60 && $v['responsetime'] <= 1000*180)?1:0;
            $sum_180s += ($v['responsetime'] > 1000*180 && $v['responsetime'] <= 1000*300)?1:0;
            $sum_300s += ($v['responsetime'] > 1000*300)?1:0;
        }

        //时间分布
        $arrTd = array(
            '0ms~100ms' => $sum_0ms,
            '100ms~500ms' => $sum_100ms,
            '500ms~1000ms' => $sum_500ms,
            '1s~10s' =>  $sum_1s,
            '10s~30s' => $sum_10s,
            '30s~60s' => $sum_30s,
            '60s~180s' => $sum_60s,
            '180s~300s' => $sum_180s,
            '300s'.$translate->getTranslateBySymbol('above') => $sum_300s, // 以上
        );

        $data = [
            'code'=> 'T',
            'td' =>['time' => array_keys($arrTd), 'tdData' => array_values($arrTd)],
            'rt'=>['time' => array_keys($arrRt), 'rtData' => array_values($arrRt)],
            'status'=>['time' => array_keys($arrRt),'statusData'=>[ 'normalData' => array_values($arrNormal)]]
        ];

        unset($arrRt);
        unset($arrNormal);
        return json_encode($data);
    }
}
