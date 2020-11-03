<?php

namespace app\modelLogs;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;
use app\logic\common\CvsHelper;


/**
 * This is the model class for table "t_cclogs".
 *
 * @property integer $id
 * @property string $AuditLogUniqueID
 * @property string $LogDateTime
 * @property string $CountryCode
 * @property string $RegionCode
 * @property string $City
 * @property string $SourceIP
 * @property string $SourcePort
 * @property string $DestinationIP
 * @property string $DestinationPort
 * @property string $Referer
 * @property string $UserAgent
 * @property string $HttpMethod
 * @property string $Url
 * @property string $HttpProtocol
 * @property string $Host
 * @property string $RequestContentType
 * @property string $ResponseContentType
 * @property string $HttpStatusCode
 * @property string $GeneralMsg
 * @property string $Rulefile
 * @property string $RuleID
 * @property string $MatchData
 * @property string $Rev
 * @property string $Msg
 * @property string $Severity
 * @property string $Tag
 * @property string $Status
 */
class CcLogs extends BaseModel
{
    public static function tableName()
    {
        return 't_cclogs';
    }

    public static function getDb()
    {
        return Yii::$app->get('dbLogs');
    }

    public function rulesSource()
    {
        return [
            [['AuditLogUniqueID', 'LogDateTime', 'SourceIP', 'DestinationIP', 'Rulefile'], 'required'],
            [['LogDateTime'], 'safe'],
            [['AuditLogUniqueID'], 'string', 'max' => 24],
            [['CountryCode'], 'string', 'max' => 3],
            [['RegionCode', 'SourcePort', 'DestinationPort', 'HttpMethod', 'Status'], 'string', 'max' => 8],
            [['City'], 'string', 'max' => 32],
            [['SourceIP', 'DestinationIP'], 'string', 'max' => 15],
            [['Referer', 'UserAgent', 'Host', 'RequestContentType', 'ResponseContentType', 'Rulefile', 'MatchData'], 'string', 'max' => 255],
            [['Url', 'GeneralMsg'], 'string', 'max' => 512],
            [['HttpProtocol', 'Severity'], 'string', 'max' => 16],
            [['HttpStatusCode'], 'string', 'max' => 4],
            [['RuleID'], 'string', 'max' => 6],
            [['Rev', 'Msg'], 'string', 'max' => 128],
            [['Tag'], 'string', 'max' => 64],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'AuditLogUniqueID' => 'AuditLogUniqueID',
            'LogDateTime' => '攻击时间',
            'CountryCode' => '地理位置',
            'RegionCode' => '地理位置',
            'City' => '地理位置',
            'SourceIP' => '源IP地址',
            'SourcePort' => '源端口',
            'DestinationIP' => 'DestinationIP',
            'DestinationPort' => '目标端口',
            'Referer' => 'Referer',
            'UserAgent' => 'User Agent',
            'HttpMethod' => 'HTTP类型',
            'Url' => 'Url',
            'HttpProtocol' => 'Http Protocol',
            'Host' => '目标主机',
            'RequestContentType' => 'RequestContentType',
            'ResponseContentType' => 'ResponseContentType',
            'HttpStatusCode' => 'HttpStatusCode',
            'GeneralMsg' => 'GeneralMsg',
            'Rulefile' => 'Rulefile',
            'RuleID' => 'Rule ID',
            'MatchData' => '匹配内容',
            'Rev' => 'Rev',
            'Msg' => '一般信息',
            'Severity' => '危害等级',
            'Tag' => 'Tag',
            'Status' => '拦截方式',
        ];
    }


    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => ['Severity', 'SourceIP', 'Host', 'DestinationPort', 'Status', 'HttpMethod',],
            '~' => ['Url',],
            '-time' => ['LogDateTime',],
        ]);
        return ['query' => $query];
    }

    public function ListSearch()
    {
        return [
            'field' => [
                'LogDateTime' => ['type' => 'betweenDateTime', 'format' => 'yyyy-MM-dd HH:mm:ss'],
                'Severity' => AdminListConfig::returnSelect('select', SL::severityArr(true, true), false),
                'SourceIP',
                'Host',
                'DestinationPort',
                'Status' => SelectList::wafActionCatArr('select'),
                'HttpMethod' => SelectList::wafHttpTypeSetArr('select'),
                'Url',
            ],
            'key' => $this->modelName,
            'model' => $this,
        ];
    }

    public function ListTable()
    {
        return [
            'field' => [
                'LogDateTime',
                'Status' => ['type' => 'switch', 'val' => SelectList::wafActionCatArr('switch')],
                'Severity' => ['type' => 'switch', 'val' => SL::severityArr(true, true)],
                'SourceIP',
                'City' => ['type' => 'callback', 'val' => function($obj, $val){
                    return \app\logic\waf\helpers\WafModels::getCountry($obj->CountryCode, $obj->RegionCode, $obj->City);
                }],
                'Host', 'DestinationPort',
            ],
            'model' => $this,
            'customStr' => \Yii::$app->view->renderFile('@app/views/cc-logs/html.php'),
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

        $SeverityArr = SL::severityArr(true, true);
        $ActionCatArr = SL::actionCatArr();

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
                    $item->LogDateTime,
                    $ActionCatArr[$item->Status],
                    $SeverityArr[$item->Severity],
                    $item->SourceIP,
                    \app\logic\waf\helpers\WafModels::getCountry($item->CountryCode, $item->RegionCode, $item->City),
                    $item->Host,
                    $item->DestinationPort,
                    $item->HttpMethod,
                    $item->Url,
                    $item->Msg,
                    $item->MatchData,
                ];
            }
        }

        #导出所有数据
        $head = [
            'attackTime',#攻击时间
            'interceptionMode',#拦截方式
            'hazardGrade',#危害等级
            'sourceIpAddress',#源IP地址
            'geographicalPosition',#地理位置
            'destinationHost',#目标主机
            'destinationPort',#目标端口
            'HTTP',
            'URL',
            'generalInformation',#一般信息
            'matchingContent',#匹配内容
        ];
        foreach ($head as $k => $v){
            $head[$k] = $translate->getTranslateBySymbol($v);
        }
        $CvsHepler = new CvsHelper();
        $CvsHepler->exportFileName('cc logs');
        $CvsHepler->exportHead($head);
        $CvsHepler->exportBody($data);
    }

    #根据RuleID返回规则信息
    public static function getDetail()
    {
        #根据realid返回规则的type与action
        $fun = function($realid)
        {
            $rst = \app\models\Rules::find()->where(['realid'=> $realid])->asArray()->all();
            if( !empty($rst) ) return $rst[0];

            $rst = \app\models\RulesCustom::find()->where(['realid'=> $realid])->asArray()->all();
            if( !empty($rst) ) return $rst[0];

            $rst = \app\models\BaseAccessCtrl::find()->where(['realid'=> $realid])->asArray()->all();
            if( !empty($rst) ) return $rst[0];

            return '';
        };

        $id = Yii::$app->request->post('id');

        $model =  self::find()->where(['id'=>$id])->asArray()->all();
        $model = $model[0];

        // Array([id] => 2, [realid] => 330002, [priority] => 1, [name] => https://www.test90_3.com/index.php, [desc] =>, [severity] => 0, [action] => deny, [status] => 1, [httpdata] => 1, [httptype] => GET, [matchdata] => URI, [matchalgorithm] => 0, [keywords] => index.php, [type] => CUSTOM)
        $RuleInfo = $fun($model['RuleID']);

        // 攻击类别
        $RuleCatArr = SL::ruleCatArr();

        $ruleCatName = '';
        if( isset($RuleInfo['type']) && strlen($RuleInfo['type'])>0 )
        {
            $ruleCatName = $RuleCatArr[$RuleInfo['type']];
        }

        $data['ruleCatName'] = $ruleCatName;  // 规则模块
        $data['name'] = isset($RuleInfo['name'])?$RuleInfo['desc']:'';  // 规则名称
        $data['Msg'] = $model['Msg']; // 一般信息
        $data['MatchData'] = $model['MatchData']; //匹配内容
        $data['RuleID'] = $model['RuleID']; //规则ID

        return json_encode($data);
    }
}
