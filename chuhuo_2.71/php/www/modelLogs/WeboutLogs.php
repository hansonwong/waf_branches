<?php

namespace app\modelLogs;

use Yii;
use app\logic\model\BaseModel;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;
use app\logic\common\CvsHelper;

/**
 * This is the model class for table "t_weboutlogs".
 *
 * @property integer $id
 * @property string $dt
 * @property string $sip
 * @property string $dip
 * @property string $CountryCode
 * @property string $RegionCode
 * @property string $City
 * @property string $sport
 * @property string $dport
 * @property integer $action
 * @property integer $number
 */
class WeboutLogs extends BaseModel
{
    public static function tableName()
    {
        return 't_weboutlogs';
    }

    public static function getDb()
    {
        return Yii::$app->get('dbLogs');
    }

    public function rulesSource()
    {
        return [
            [['dt'], 'safe'],
            [['action', 'number'], 'integer'],
            [['sip', 'dip'], 'string', 'max' => 15],
            [['CountryCode'], 'string', 'max' => 3],
            [['RegionCode'], 'string', 'max' => 8],
            [['City'], 'string', 'max' => 32],
            [['sport', 'dport'], 'string', 'max' => 5],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'dt' => '日期',
            'sip' => '源IP地址',
            'dip' => '目标IP地址',
            'CountryCode' => '地理位置',
            'RegionCode' => '地理位置',
            'City' => '地理位置',
            'sport' => '源端口',
            'dport' => '目标端口',
            'action' => '执行动作',
            'number' => 'Number',
        ];
    }

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => ['action', 'sport', 'dport',],
            '~' => ['sip', 'dip',],
            '-time' => ['dt',],
        ]);
        return ['query' => $query];
    }

    public function ListSearch()
    {
        return [
            'field' => [
                'dt' => ['type' => 'betweenDateTime', 'format' => 'yyyy-MM-dd HH:mm:ss'],
                'sip',
                'sport',
                'dip',
                'dport',
                'action' => SelectList::passAndIntercept('select'),
            ],
            'key' => $this->modelName,
            'model' => $this,
        ];
    }

    public function ListTable()
    {
        $addBlackList = Yii::$app->sysLanguage->getTranslateBySymbol('addBlackList');
        $addWhiteList = Yii::$app->sysLanguage->getTranslateBySymbol('addWhiteList');
        return [
            'publicButton' => [
                'create' => false,
                ['button' => "<input type=button class='btn c_b btn_hmd' value='{$addBlackList}' onclick='statusChange(0, 1);'>", 'authorityPass' => true],
                ['button' => "<input type=button class='btn c_o btn_bmd' value='{$addWhiteList}' onclick='statusChange(0, 0);'>", 'authorityPass' => true],
            ],
            'field' => [
                'dt',
                'sip',
                'sport',
                'dip',
                'dport',
                'City' => ['type' => 'callback', 'val' => function($obj, $val){
                    return \app\logic\waf\helpers\WafModels::getCountry($obj->CountryCode, $obj->RegionCode, $obj->City);
                }],
                'action' => ['type' => 'switch', 'val' => SelectList::passAndIntercept('switch')],
            ],
            'model' => $this,
            'customStr' => \Yii::$app->view->renderFile('@app/views/rule-custom-defend-policy/list-component.php',[
                'config' => ['url' => 'create'],
            ]),
        ];
    }

    //导出记录
    public static function export(){
        $translate = Yii::$app->sysLanguage;
        $pageSize = 1000;#数据分批获取数量
        $data = [];#所有数据

        #获取分页信息
        $table = new self;#数据模型对象
        $dataProvider = AdminListConfig::getActiveDataProviderSetting(
            array_merge(
                $table->search(Yii::$app->request->post()),
                ['pagesize' => $pageSize, 'page' => 0]
            )
        );
        $pagination = $dataProvider->getPagination();
        $dataProvider->getModels();
        $pageCount = $pagination->getPageCount();
        #获取分页信息END

        $passAndIntercept = SL::passAndIntercept();

        #获取所有数据
        for($i = 0; $i < $pageCount; $i++){
            $dataProvider = AdminListConfig::getActiveDataProviderSetting(
                array_merge(
                    $table->search(Yii::$app->request->post()),
                    ['pagesize' => $pageSize, 'page' => $i]
                )
            );
            $dataList = $dataProvider->getModels();

            foreach($dataList as $item){
                $data[] = [
                    $item->dt,
                    $item->sip,
                    $item->sport,
                    $item->dip,
                    $item->dport,
                    $passAndIntercept[$item->action],
                ];
            }
        }

        #导出所有数据
        $head = [
            'date',#日期
            'sourceIpAddress',#源IP
            'sourcePort',#源端口
            'targetIpAddress',#目标IP地址
            'destinationPort',#目标端口
            'executionAction',#执行动作
        ];

        foreach ($head as $k => $v){
            $head[$k] = $translate->getTranslateBySymbol($v);
        }
        $CvsHepler = new CvsHelper();
        $CvsHepler->exportFileName($translate->getTranslateBySymbol('illegalOutLinkLog').date('Y-m-d H:i:s'));
        $CvsHepler->exportHead($head);
        $CvsHepler->exportBody($data);
    }

    #添加黑白名单
    public static function updateBlackAndWhite(){
        $model = new self;
        $query = Yii::$app->request->bodyParams;
        $id = $query['id'];
        $status = $query['status'];
        if(!is_array($id)) return false;
        foreach($id as $v)
        {
            $item = $model->findOne($v);
            $count = \app\models\WebServerOutBound::find()->where([
                'sip' => $item->sip, 'dip' => $item->dip, 'dport' => $item->dport
            ])->count();
            if($count<1)
            {
                $model = new \app\models\WebServerOutBound;
                $model['is_use']=$status;
                $model['sip']=$item->sip;
                $model['dip']=$item->dip;
                $model['dport']=$item->dport;
                $model->save();
            }
        }

        Yii::$app->wafHelper->pipe('CMD_WEBOUTRULE');
        Yii::$app->sysJsonMsg->msg(true, '', false);
    }
}
