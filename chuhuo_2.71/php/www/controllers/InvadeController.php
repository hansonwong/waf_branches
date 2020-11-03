<?php
namespace app\controllers;

use Yii;
use app\logic\BaseController;
use app\modelLogs\AlertLogs;
use app\models\Rules;
use app\models\RuleModel;
use app\models\RulesCustom;
use app\models\SelfStudyRule;
use app\models\WebSite;
use app\models\BaseAccessCtrl;
use app\logic\waf\models\SelectList;
use yii\helpers\Html;
use app\widget\AdminListConfig;
use yii\data\Pagination;
use app\logic\waf\helpers\WafModels;

/**
 *  日志报表 - 日志 - 入侵日志
 * Class InvadeController
 * @package app\controllers
 */
class InvadeController extends BaseController
{
    // 拦截方式
    public $ActionCatArr = [];

    // 告警等级
    public $SeverityArr = [];

    // 攻击类别
    public $RuleCatArr = [];

    // HTTP请求类型
    public $HttpTypeSetArr = [];

    public function init()
    {
        parent::init();
        ignore_user_abort(TRUE);
        @set_time_limit(0);
        @ini_set("memory_limit", "1024M");
    }

    /**
     * 列表
     * @return string
     */
    public function actionIndex()
    {
        // 返回模板
        if( Yii::$app->request->isGet )
        {
            // 危害等级
            if( empty($this->SeverityArr) )
            {
                $this->SeverityArr = SelectList::severityArr(true, true);
            }
            // 拦截方式
            if( empty($this->ActionCatArr) )
            {
                $this->ActionCatArr = SelectList::actionCatArr();
            }
            // HTTP请求类型
            if( empty($this->HttpTypeSetArr) )
            {
                $this->HttpTypeSetArr = SelectList::httpTypeSetArr();
            }
            // 攻击类别
            if( empty($this->RuleCatArr) )
            {
                $this->RuleCatArr = SelectList::ruleCatArr();
            }
            unset($this->RuleCatArr['CC']); // 去除CC攻击类型

            $model = '';
            return $this->render('index', [
                'model' => $model,
                'RuleCatArr'=>$this->RuleCatArr,
                'SeverityArr'=>$this->SeverityArr,
                'ActionCatArr'=>$this->ActionCatArr,
                'HttpTypeSetArr'=>$this->HttpTypeSetArr,
            ]);
        }

        // 返回 详情
        if( Yii::$app->request->get('op')=='detail' ) return $this->detail();

        // 返回头部数据
        if( Yii::$app->request->get('op')=='header' ) return $this->GridHeader();

        // 返回表格数据
        return $this->GridBody();
    }

    /**
     * 返回列表头名字
     *[
     *{"sTitle":"攻击时间","data":"time","width":220},
     *{"sTitle":"攻击类型","data":"type"},
     *{"sTitle":"拦截方式","data":"way"},
     *{"sTitle":"危害等级","data":"grade"},
     *{"sTitle":"源IP地址","data":"yuanIP","width":200},
     *{"sTitle":"地理位置","data":"local"},
     *{"sTitle":"目标主机","data":"host","width":200},
     *{"sTitle":"目标端口","data":"port"},
     *{"sTitle":"HTTP","data":"http"},
     *{"sTitle":"URL","data":"url"},
     *{"sClass":"btn_edit","bVisible":false,"data":""},
     *{"sClass":"btn_view","bVisible":false,"data":""},
     *{"sClass":"btn_del","bVisible":false,"data":""}
     *]
     *]
     * @return string
     */
    private function GridHeader()
    {
        $title = [
            ["sTitle"=>$this->translate->getTranslateBySymbol('attackTime'),"data"=>"LogDateTime","minWidth"=>170],  //攻击时间
            ["sTitle"=>$this->translate->getTranslateBySymbol('attackType'),"data"=>"ruleCatName", "minWidth"=>80],  // 攻击类型
            ["sTitle"=>$this->translate->getTranslateBySymbol('interceptionMode'),"data"=>"actionCatName", "minWidth"=>80], //拦截方式
            ["sTitle"=>$this->translate->getTranslateBySymbol('hazardGrade'),"data"=>"SeverityName", "minWidth"=>70],  //危害等级
            ["sTitle"=>$this->translate->getTranslateBySymbol('sourceIpAddress'),"data"=>"SourceIP", "minWidth"=>140],  //源IP地址
            ["sTitle"=>$this->translate->getTranslateBySymbol('sourcePort'),"data"=>"SourcePort", "minWidth"=>70],  // 源端口
            ["sTitle"=>$this->translate->getTranslateBySymbol('geographicalPosition'),"data"=>"City","minWidth"=>100],  //地理位置
            ["sTitle"=>$this->translate->getTranslateBySymbol('destinationHost'),"data"=>"Host", "minWidth"=>140],  //目标主机
            ["sTitle"=>$this->translate->getTranslateBySymbol('destinationPort'),"data"=>"DestinationPort", "minWidth"=>60],  //目标端口
            ["sTitle"=>"HTTP","data"=>"HttpMethod", "minWidth"=>70],
            ["sClass"=>"btn_del","bVisible"=>false,"data"=>""],
            ["sClass"=>"btn_join","bVisible"=>false,"data"=>""],
            ["sClass"=>"btn_outage","bVisible"=>false,"data"=>""]
        ];
        return json_encode($title);
    }

    /**
    {
    "data":[
    {"rulesID":"2005190","way":"默认动作","grade":"高危","beizhu":"检测请求行中是否包含/models/category.php并且catid 参数中是否带有 SQL语句（select from）如果是，则判断为 Joomla! SQL注入尝试。将会阻断并设置相关参数","type":"CM漏洞攻击","serverSelect":"1","time":"2016-01-30 10:00:00","rulesName":"Joomla! SQL注入尝试（1）","sTypeName":"CMS漏洞攻击 (387个规则集)"},
    {"rulesID":"2005190","way":"默认动作","grade":"高危","beizhu":"站点组","type":"CM漏洞攻击","serverSelect":"1","time":"2016-01-30 10:00:00","rulesName":"规则名称3","sTypeName":"组3"}
    ],
    "Total":"16"
    }
     * @return string
     */
    private function GridBody()
    {
        // 接收的页数
        $page = intval(Yii::$app->request->post('page',0));
        $page = $page>0?$page-1:$page;
        $pageSize = intval(Yii::$app->request->post('pagesize',20));

        // 排序
        $sortName = Yii::$app->request->post('sortname','LogDateTime');
        $sortOrder = Yii::$app->request->post('sortorder','DESC');
        $orderBy = "{$sortName} {$sortOrder}";
        if( strlen($orderBy)<1 )
        {
            $orderBy = "LogDateTime DESC";
        }

        // 整合搜索条件
        $whereStr = $this->getWhereSql('post');

        // 处理分页
        $pagination = new Pagination(['totalCount' => AlertLogs::find()->where($whereStr)->count()]);
        $pagination->page = $page;
        $pagination->pageSize = $pageSize;

        // 危害等级
        if( empty($this->SeverityArr) )
        {
            $this->SeverityArr = SelectList::severityArr(true,true);
        }
        // 拦截方式
        if( empty($this->ActionCatArr) )
        {
            $this->ActionCatArr = SelectList::actionCatArr();
        }

        $list = [];
        // 查询字段
        $select = "*";
        $model =  AlertLogs::find()->select($select)->where($whereStr)->orderBy($orderBy)->offset($pagination->offset)->limit($pagination->limit)->asArray()->all();
        foreach( $model as $v )
        {
            $url =strlen($v['Url'])>16?substr($v['Url'],0,16).'...':$v['Url'];
            $url ="<span title='{$v['Url']}'>{$url}</span>";

            // 攻击类型
            $ruleCatName = $this->getruleCatName($v['AttackType']);

            // 整理输出数据
            $list[] = [
                "id" => $v['id'],
                "RuleID" => $v['RuleID'],
                "LogDateTime" => $v['LogDateTime'],
                "ruleCatName" => $ruleCatName,
                "actionCatName" => $this->ActionCatArr[$v['Status']],
                "SeverityName" => $this->SeverityArr[$v['Severity']],
                "SourceIP" => $v['SourceIP'],
                "SourcePort" => $v['SourcePort'],
                "City" => WafModels::getCountry($v['CountryCode'], $v['RegionCode'], $v['City']),
                "Host" => $v['Host'],
                "DestinationPort" => $v['DestinationPort'],
                "HttpMethod" => $v['HttpMethod'],
                "Url" => $url,
            ];
        }

        $data = [
            'data' => $list,
            'total' => $pagination->totalCount,
            'page' => $pagination->offset+1,
            'pagesize' => $pageSize,
        ];
        return json_encode($data);
    }

    /**
     * 根据RuleID返回规则信息
     * @return string
     */
    private function detail()
    {
        $id = Yii::$app->request->post('id');

        $model =  AlertLogs::find()->where(['id'=>$id])->asArray()->one();

        // Array([id] => 2, [realid] => 330002, [priority] => 1, [name] => https://www.test90_3.com/index.php, [desc] =>, [severity] => 0, [action] => deny, [status] => 1, [httpdata] => 1, [httptype] => GET, [matchdata] => URI, [matchalgorithm] => 0, [keywords] => index.php, [type] => CUSTOM)
        $RuleInfo = $this->getRuleInfoNameByRealId($model['RuleID']);

        // 攻击类别
        if( empty($this->RuleCatArr) )
        {
            $this->RuleCatArr = SelectList::ruleCatArr();
        }

        $ruleCatName = '';
        if( isset($RuleInfo['type']) && strlen($RuleInfo['type'])>0 )
        {
            $ruleCatName = $this->RuleCatArr[$RuleInfo['type']];
        }

        $data['ruleCatName'] = Html::encode($ruleCatName);  // 规则模块
        $data['name'] = Html::encode(isset($RuleInfo['name'])?$RuleInfo['name']:$RuleInfo['desc']);  // 规则名称
        $data['Msg'] = Html::encode($model['Msg']); // 一般信息
        $data['MatchData'] = Html::encode($model['MatchData']); //匹配内容
        $data['RuleID'] = $model['RuleID']; //规则ID
        $data['url'] = Html::encode($model['Url']);

        return json_encode($data);
    }

    /**
     * 删除 与 清空
     * @throws \yii\base\ExitException
     */
    public function actionDelete()
    {
        // 条件清空
        if( Yii::$app->request->get('op')=='dump' )
        {
            $this->dump();
        }

        // 以下为删除
        $id_arr = Yii::$app->request->post('id_arr');
        $id_arr = json_decode($id_arr);
        // 过滤非数字的内容
        $id_arr = array_filter($id_arr, 'is_numeric');
        if( empty($id_arr) )
        {
            $info = $this->translate->getTranslateBySymbol('thereIsNoSelectionOfDataToDelete');//'没有选择需要删除的数据';
            AdminListConfig::returnSuccessFieldJson('F', $info, true);
        }

        $id_str = implode(",", $id_arr);
        if( AlertLogs::deleteAll("id in ({$id_str})") === false )
        {
            $info = $this->translate->getTranslateBySymbol('deleteFailed');//'删除失败';
            AdminListConfig::returnSuccessFieldJson('F', $info, true);
        }

        $info = $this->translate->getTranslateBySymbol('operationSuccess');//'操作成功';
        AdminListConfig::returnSuccessFieldJson('T', $info, true);
    }

    /**
     * 根据条件清空数据
     * @throws \yii\base\ExitException
     */
    private function dump()
    {
        $searchData = Yii::$app->request->post('searchData');
        $searchData = json_decode($searchData, true);

        // 精确查询
        $whereStr = "";
        // 攻击时间
        if( strtotime($searchData['keywordStartDate'])>0 )
        {
            $whereStr = "AND LogDateTime >= '{$searchData['keywordStartDate']}' ";
        }
        if( strtotime($searchData['keywordEndDate'])>0 && strtotime($searchData['keywordEndDate'])>=strtotime($searchData['keywordStartDate']) )
        {
            $whereStr .= "AND LogDateTime <= '{$searchData['keywordEndDate']}' ";
        }
        // 攻击类型
        if( strlen($searchData['type'])>0 )
        {
            $whereStr .= "AND AttackType='{$searchData['type']}' ";
        }
        // 危害等级
        if( strlen($searchData['Severity'])>0 )
        {
            $whereStr .= "AND Severity='{$searchData['Severity']}' ";
        }
        // 源IP地址
        if( strlen($searchData['SourceIP'])>0 )
        {
            $whereStr .= "AND SourceIP LIKE '%{$searchData['SourceIP']}%' ";
        }
        // 源端口
        if( strlen($searchData['SourcePort'])>0 )
        {
            $whereStr .= "AND SourcePort='{$searchData['SourcePort']}' ";
        }
        // 目标IP
        if( strlen($searchData['DestinationIP'])>0 )
        {
            $whereStr .= "AND DestinationIP='{$searchData['DestinationIP']}' ";
        }
        // 目标端口
        if( strlen($searchData['DestinationPort'])>0 )
        {
            $whereStr .= "AND DestinationPort='{$searchData['DestinationPort']}' ";
        }
        // 拦截方式
        if( strlen($searchData['Status'])>0 )
        {
            $whereStr .= "AND Status='{$searchData['Status']}' ";
        }
        // HTTP类型
        if( strlen($searchData['HttpMethod'])>0 )
        {
            $whereStr .= " AND HttpMethod='{$searchData['HttpMethod']}'";
        }
        // 目标主机
        if( strlen($searchData['Host'])>0 )
        {
            $whereStr .= "AND Host LIKE '%{$searchData['Host']}%' ";
        }

        if( AlertLogs::find()->count() <1 )
        {
            $info = $this->translate->getTranslateBySymbol('operationSuccess');  //操作成功
            AdminListConfig::returnSuccessFieldJson('T', $info, true);
        }

        $whereStr = '1 '.$whereStr;
        if( AlertLogs::deleteAll($whereStr) === false )
        {
            $info = $this->translate->getTranslateBySymbol('deleteFailed');   //删除失败
            AdminListConfig::returnSuccessFieldJson('F', $info, true);
        }

        $info = $this->translate->getTranslateBySymbol('operationSuccess');  //操作成功
        AdminListConfig::returnSuccessFieldJson('T', $info, true);
    }

    /**
     * 更新
     * @param int $id
     * @return mixed|void
     * @throws \yii\base\ExitException
     */
    public function actionUpdate($id=0)
    {
        // 加入防误报
        if( Yii::$app->request->get('op')=='addFwb' )
        {
            $this->addFwb();
        }

        // 停用对应规则
        if( Yii::$app->request->get('op')=='stopRule' )
        {
            $this->stopRule();
        }
    }

    /**
     * 加入防误报
     * @throws \yii\base\ExitException
     */
    private function addFwb()
    {
        $id_arr = Yii::$app->request->post('id_arr');
        $id_arr = json_decode($id_arr);
        // 过滤非数字的内容
        $id_arr = array_filter($id_arr, 'is_numeric');
        if( empty($id_arr) )
        {
            $info = $this->translate->getTranslateBySymbol('noChoiceNeedsToBeAddedToMisinformation');  //没有选择需要加入防误报的数据
            AdminListConfig::returnSuccessFieldJson('F', $info, true);
        }

        $numSuccess = 0; // 记录成功的
        $numFailure = 0; // 记录失败的
        foreach( $id_arr as $v )
        {
            $v = intval($v);

            $AlertLogsModel =  AlertLogs::find()->select(['id','RuleID','SourceIP','SourcePort','Url','Host'])->where(['id'=>$v])->asArray()->all();
            $AlertLogsModel = $AlertLogsModel[0];

            $rulesModel = Rules::findOne($AlertLogsModel['RuleID']);
            if( !empty($rulesModel) )
            {
                $uri = str_replace($AlertLogsModel['Host'], "", $AlertLogsModel['Url']);
                $new_uri = strstr($uri, '/');

                $SelfStudyRuleModel = new SelfStudyRule;
                $SelfStudyRuleModel->ruleid = $rulesModel['id'];
                $SelfStudyRuleModel->realruleid = $rulesModel['realid'];
                $SelfStudyRuleModel->is_use = 1;
                $SelfStudyRuleModel->uri = $new_uri;
                $SelfStudyRuleModel->host = $AlertLogsModel['Host'];
                $SelfStudyRuleModel->sourceip = $AlertLogsModel['SourceIP'];
                $SelfStudyRuleModel->sourceport = $AlertLogsModel['SourcePort'];
                if( $SelfStudyRuleModel->save() )
                {
                    $numSuccess++;
                }
                else
                {
                    $numFailure++;
                }
            }
        }

        // 写入命名管道
        Yii::$app->wafHelper->pipe('CMD_NGINX');

        //操作成功, 共成功处理符合防误报条件的{$numSuccess}条日志, 失败的{$numFailure}条
        $info = sprintf($this->translate->getTranslateBySymbol('operationSuccessfulFalseAlarmConditionTips'),$numSuccess,$numFailure);
        AdminListConfig::returnSuccessFieldJson('T', $info, true);
    }

    /**
     * 停用对应规则
     * @throws \yii\base\ExitException
     */
    private function stopRule()
    {
        $id = intval(Yii::$app->request->post('id'));
        if( $id<1 )
        {
            $info = $this->translate->getTranslateBySymbol('parameterError');  //参数不对
            AdminListConfig::returnSuccessFieldJson('F', $info, true);
        }

        // 当日志是反向代理才会才会停用模板规则，其它就直接停用内置规则
        $AlertLogsModel = AlertLogs::findOne($id);
        if( $AlertLogsModel['LogSource']!='proxy' )
        {
            // 直接停用 内置规则库 与 规则模板库
            $rst = $this->stopRulesByRealId($AlertLogsModel['RuleID']);
            if( $rst['code'] != 'T' )
            {
                $info = $rst['info'];
                AdminListConfig::returnSuccessFieldJson('F', $info, true);
            }

            Yii::$app->wafHelper->pipe('CMD_NGINX');
            $info = $this->translate->getTranslateBySymbol('operationSuccess');  //操作成功
            AdminListConfig::returnSuccessFieldJson('T', $info, true);
        }

        // 获取  站点组——》站点数据,  根据 Host目标主机,DestinationPort目标端口
        $rst = $this->getWebsiteInfo($AlertLogsModel->Host, $AlertLogsModel->DestinationPort);
        if( $rst['code'] != 'T' )
        {
            $info = $rst['info'];
            AdminListConfig::returnSuccessFieldJson('F', $info, true);
        }

        $selfRuleModelId = $rst['data']['selfRuleModelId']; // 站点模板ID
        $ruleModelId = $rst['data']['ruleModelId']; // 站点组模板ID

        // 有对应站点模板，停用站点模板对应规则
        if( $selfRuleModelId>0 )
        {
            $rst = $this->stopRulesByRuleModelId($selfRuleModelId, $AlertLogsModel->RuleID);
            if( $rst['code'] == 'T' )
            {
                // 写入命名管道
                Yii::$app->wafHelper->pipe('CMD_NGINX');
                $info = $this->translate->getTranslateBySymbol('operationSuccess');  //操作成功
                AdminListConfig::returnSuccessFieldJson('T', $info, true);
            }
        }

        // 没有站点模板，有站点组模板，停用站点组模板对应规则
        if( $ruleModelId>0 )
        {
            $rst = $this->stopRulesByRuleModelId($ruleModelId, $AlertLogsModel->RuleID);
            if( $rst['code'] == 'T' )
            {
                // 写入命名管道
                Yii::$app->wafHelper->pipe('CMD_NGINX');
                $info = $this->translate->getTranslateBySymbol('operationSuccess');   //操作成功
                AdminListConfig::returnSuccessFieldJson('T', $info, true);
            }
        }

        // 直接停用 内置规则库 与 规则模板库
        $rst = $this->stopRulesByRealId($AlertLogsModel['RuleID']);
        if( $rst['code'] != 'T' )
        {
            $info = $rst['info'];
            AdminListConfig::returnSuccessFieldJson('F', $info, true);
        }

        Yii::$app->wafHelper->pipe('CMD_NGINX');
        $info = $this->translate->getTranslateBySymbol('operationSuccess');   //操作成功
        AdminListConfig::returnSuccessFieldJson('T', $info, true);
    }

    /**
     * 导出
     */
    public function actionExportData()
    {
        // 精确查询 条件
        $whereStr = $this->getWhereSql();

        // 导出的文件名
        $file = $this->translate->getTranslateBySymbol('invadeLog').date('Y-m-d H:i:s');  //入侵日志

        header('Content-Type: application/vnd.ms-excel');
        header("Content-Disposition: attachment;filename=\"".iconv('utf-8', 'gbk', $file).".csv\"");
        header('Cache-Control: max-age=0');

        // 打开PHP文件句柄，php://output 表示直接输出到浏览器
        $fp = fopen('php://output', 'a');

        // 表头 ['攻击时间','攻击类型','拦截方式','危害等级','源IP地址','地理位置','目标主机','目标端口','HTTP','URL','一般信息','匹配内容'];
        $head = [
            $this->translate->getTranslateBySymbol('attackTime'),
            $this->translate->getTranslateBySymbol('attackType'),
            $this->translate->getTranslateBySymbol('interceptionMode'),
            $this->translate->getTranslateBySymbol('hazardGrade'),
            $this->translate->getTranslateBySymbol('sourceIpAddress'),
            $this->translate->getTranslateBySymbol('geographicalPosition'),
            $this->translate->getTranslateBySymbol('destinationHost'),
            $this->translate->getTranslateBySymbol('destinationPort'),
            'HTTP',
            'URL',
            $this->translate->getTranslateBySymbol('generalInformation'),
            $this->translate->getTranslateBySymbol('matchingContent')
        ];
        foreach ($head as $i => $v)
        {
            // CSV的Excel支持GBK编码，一定要转换，否则乱码
            $head[$i] = iconv('utf-8', 'gbk', $v);
        }

        // 将数据通过fputcsv写到文件句柄
        fputcsv($fp, $head);

        // 危害等级
        if( empty($this->SeverityArr) )
        {
            $this->SeverityArr = SelectList::severityArr(true,true);
        }
        // 拦截方式
        if( empty($this->ActionCatArr) )
        {
            $this->ActionCatArr = SelectList::actionCatArr();
        }

        // 处理分页
        $pagination = new Pagination(['totalCount' => AlertLogs::find()->where($whereStr)->count()]);
        $pagination->pageSize = 1000;

        while (true)
        {
            // 查询字段
            $model =  AlertLogs::find()->where($whereStr)->orderBy('id DESC')->offset($pagination->offset)->limit($pagination->limit)->asArray()->all();
            //判断如果为空就退出循环
            if( empty($model) ) break;
            foreach( $model as $v )
            {
                // 攻击类型
                $ruleCatName = $this->getruleCatName($v['AttackType']);

                // 整理输出数据
                fputcsv($fp, [
                    $v['LogDateTime'],
                    iconv('utf-8', 'gbk', $ruleCatName),
                    iconv('utf-8', 'gbk',$this->ActionCatArr[$v['Status']]),
                    iconv('utf-8', 'gbk',$this->SeverityArr[$v['Severity']]),
                    $v['SourceIP'],
                    iconv('utf-8', 'gbk',WafModels::getCountry($v['CountryCode'], $v['RegionCode'], $v['City'])),
                    $v['Host'],
                    $v['DestinationPort'],
                    $v['HttpMethod'],
                    $v['Url'],
                    $v['Msg'],
                    $v['MatchData'],
                ]);
            }

            //刷新一下输出buffer，防止由于数据过多造成问题
            ob_flush();
            flush();

            $pagination->page++;
            // 超过20页退出
            if( $pagination->page==20 ) break;
        }
    }

    /**
     * 攻击类别 名称
     * @param $AttackType
     * @return mixed|\yii\db\ActiveRecord
     */
    private function getruleCatName($AttackType)
    {
        // 攻击类别
        if( empty($this->RuleCatArr) )
        {
            $this->RuleCatArr = SelectList::ruleCatArr();
        }

        // 攻击类型
        $ruleCatName = $this->RuleCatArr[$AttackType];
        $ruleCatName = strlen($ruleCatName)<1?$this->translate->getTranslateBySymbol('custom'):$ruleCatName;  //自定义

        return $ruleCatName;
    }

    /**
     * @param string $method get|post
     * @return string
     */
    private function getWhereSql($method='get')
    {
        // 整合搜索条件
        $whereStr = '1 ';
        $LogDateTimeStart = trim(Yii::$app->request->$method('LogDateTimeStart','')); //攻击时间
        if( strtotime($LogDateTimeStart)>0 )
        {
            $whereStr .= "AND LogDateTime >= '{$LogDateTimeStart}' ";
        }
        $LogDateTimeEnd = trim(Yii::$app->request->$method('LogDateTimeEnd','')); // 攻击时间
        if( strtotime($LogDateTimeEnd)>0 && strtotime($LogDateTimeEnd)>=strtotime($LogDateTimeStart) )
        {
            $whereStr .= "AND LogDateTime <= '{$LogDateTimeEnd}' ";
        }

        // 精确查询
        $keywordStartDate = trim(Yii::$app->request->$method('keywordStartDate','')); //攻击时间
        if( strtotime($keywordStartDate)>0 )
        {
            $whereStr .= "AND LogDateTime >= '{$keywordStartDate}' ";
        }
        $keywordEndDate = trim(Yii::$app->request->$method('keywordEndDate','')); // 攻击时间
        if( strtotime($keywordEndDate)>0 && strtotime($keywordEndDate)>=strtotime($keywordStartDate) )
        {
            $whereStr .= "AND LogDateTime <= '{$keywordEndDate}' ";
        }
        $type = trim(Yii::$app->request->$method('type','')); // 攻击类型
        if( strlen($type)>0 )
        {
            $whereStr .= "AND AttackType='{$type}' ";
        }
        $Severity = trim(Yii::$app->request->$method('Severity','')); // 危害等级
        if( strlen($Severity)>0 )
        {
            $whereStr .= "AND Severity='{$Severity}' ";
        }
        $SourceIP = trim(Yii::$app->request->$method('SourceIP','')); // 源IP地址
        if( strlen($SourceIP)>0 )
        {
            $whereStr .= "AND SourceIP LIKE '%{$SourceIP}%' ";
        }
        $SourcePort = trim(Yii::$app->request->$method('SourcePort','')); // 源端口
        if( strlen($SourcePort)>0 )
        {
            $whereStr .= "AND SourcePort='{$SourcePort}' ";
        }
        $DestinationIP = trim(Yii::$app->request->$method('DestinationIP','')); // 目标IP
        if( strlen($DestinationIP)>0 )
        {
            $whereStr .= "AND DestinationIP='{$DestinationIP}' ";
        }
        $DestinationPort = trim(Yii::$app->request->$method('DestinationPort','')); // 目标端口
        if( strlen($DestinationPort)>0 )
        {
            $whereStr .= "AND DestinationPort='{$DestinationPort}' ";
        }
        $Status = trim(Yii::$app->request->$method('Status','')); // 拦截方式
        if( strlen($Status)>0 )
        {
            $whereStr .= "AND Status='{$Status}' ";
        }
        $HttpMethod = trim(Yii::$app->request->$method('HttpMethod','')); // HTTP类型
        if( strlen($HttpMethod)>0 )
        {
            $whereStr .= " AND HttpMethod='{$HttpMethod}'";
        }
        $Host = trim(Yii::$app->request->$method('Host','')); // 目标主机
        if( strlen($Host)>0 )
        {
            $whereStr .= "AND Host LIKE '%{$Host}%' ";
        }

        return $whereStr;
    }

    // 直接停用 内置规则库 与 规则模板库
    private function stopRulesByRealId($realid)
    {
        $data = array('code'=> 'F', 'info'=> $this->translate->getTranslateBySymbol('unknown'));  //未知
        $realid = intval($realid);

        //启用 1  停用 0
        $status = 0;
        // 停用内置规则
        $RulesModel = Rules::findOne($realid);
        if( $RulesModel->status != 0 )
        {
            if( Rules::updateAll(['status'=>$status], "realid= {$realid}") < 1 )
            {
                $data['info'] = $this->translate->getTranslateBySymbol('updateFailed');  //更新失败
                return $data;
            }
        }

        // 修改 规则模板设置 规则ID
        $RuleModel = RuleModel::find()->select(['id', 'rule'])->where("type=3 AND isDefault=1")->asArray()->one();
        if( empty($RuleModel) )
        {
            $data['info'] = $this->translate->getTranslateBySymbol('ruleTemplateLibraryCannotFindDefaultTemplate');  //规则模板库找不到默认模板
            return $data;
        }

        $ruleArr = json_decode($RuleModel['rule'], true);
        if( !is_array($ruleArr) )
        {
            $ruleArr = [];
        }

        if( !in_array($realid, $ruleArr) )
        {
            // 同步规则ID 到 规则模板设置
            array_push($ruleArr, "{$realid}");
            $rules = json_encode(array_unique($ruleArr));
            if( RuleModel::updateAll(['rule'=>$rules], "id={$RuleModel['id']}") < 1 )
            {
                $data['info'] = $this->translate->getTranslateBySymbol('ruleTemplateLibraryUpdateFailed'); //规则模板库更新失败
                return $data;
            }
        }

        $data['code'] = 'T';
        $data['message'] = $this->translate->getTranslateBySymbol('success');  //成功

        return $data;
    }

    // 停用 规则模板库 规则
    private function stopRulesByRuleModelId($RuleModelId, $realid)
    {
        $data = array('code'=> 'F', 'info'=> $this->translate->getTranslateBySymbol('unknown'));  //未知
        $realid = intval($realid);

        // 修改 规则模板设置 规则ID
        $RuleModel = RuleModel::find()->select(['id', 'rule'])->where("id={$RuleModelId}")->asArray()->all();
        $RuleModel = $RuleModel[0];
        if( empty($RuleModel) )
        {

            $data['info'] = $this->translate->getTranslateBySymbol('ruleTemplateLibraryCannotFindTemplate');  //规则模板库找不到模板
            return $data;
        }

        $ruleArr = json_decode($RuleModel['rule'], true);
        if( !is_array($ruleArr) )
        {
            $ruleArr = [];
        }
        // 同步规则ID 到 规则模板设置
        array_push($ruleArr, "{$realid}");
        $rules = json_encode(array_unique($ruleArr));

        if( RuleModel::updateAll(['rule'=>$rules], "id={$RuleModel['id']}") < 1 )
        {
            $data['info'] = $this->translate->getTranslateBySymbol('ruleTemplateLibraryUpdateFailed');   //规则模板库更新失败
            return $data;
        }

        $data['code'] = 'T';
        $data['message'] = $this->translate->getTranslateBySymbol('success');;  //成功

        return $data;
    }

    /**
     * Host目标主机,DestinationPort目标端口
     * @param $Host string 目标主机
     * @param $DestinationPort string 目标端口
     * @return array
     */
    private function getWebsiteInfo($Host, $DestinationPort)
    {
        $data = array('code'=> 'F', 'info'=> $this->translate->getTranslateBySymbol('unknown'));  //未知

        $Host = trim($Host);
        $DestinationPort = trim($DestinationPort);

        $whereStr = "sWebSiteName='{$Host}' AND iWebSitePort='{$DestinationPort}'";
        $model = WebSite::find()->select(['id','ruleModelId','selfRuleModelId'])->where($whereStr)->asArray()->all();
        $model = $model[0];
        if( empty($model) )
        {
            $data['info'] = $this->translate->getTranslateBySymbol('correspondingSiteDoesNotExistTips');   //所对应的站点不存在,请在“站点组管理”增加站点
            return $data;
        }

        $data['code'] = 'T';
        $data['info'] = $this->translate->getTranslateBySymbol('success');;  //成功
        $data['data'] = [
            'website_id' => $model['id'],
            'ruleModelId' => $model['ruleModelId'],
            'selfRuleModelId' => $model['selfRuleModelId'],
        ];

        return $data;
    }

    /**
     * 根据realid返回规则的type与action
     * @param $realid
     * @return mixed|string
     */
    private function getRuleInfoNameByRealId($realid)
    {
        $rst = Rules::find()->where(['realid'=> $realid])->asArray()->all();
        if( !empty($rst) ) return $rst[0];

        $rst = RulesCustom::find()->where(['realid'=> $realid])->asArray()->all();
        if( !empty($rst) ) return $rst[0];

        $rst = BaseAccessCtrl::find()->where(['realid'=> $realid])->asArray()->all();
        if( !empty($rst) ) return $rst[0];

        return '';
    }
}
