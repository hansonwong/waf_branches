<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;
/**
 * This is the model class for table "t_website".
 *
 * @property integer $id
 * @property string $sGroupName
 * @property string $sWebSiteName
 * @property string $sWebSiteIP
 * @property integer $iWebSitePort
 * @property string $sWebSiteProtocol
 * @property integer $iWebSiteGroupId
 * @property integer $ruleModelId
 * @property integer $selfRuleModelId
 * @property string $daymaxtraffic
 * @property string $dayipmaxvisit
 * @property string $modelingstartdate
 * @property integer $modelingperiod
 * @property string $modelingendday
 * @property integer $mstatus
 * @property integer $studyTime
 * @property string $beginTime
 * @property string $endTime
 * @property string $remarks
 * @property integer $isproxy
 * @property string $ddosfencetype
 * @property string $hatype
 * @property integer $type
 * @property integer $cache
 * @property integer $helthcheck
 * @property string $ssl_path1
 * @property string $ssl_path2
 * @property string $porxy_remark
 * @property string $modsec_status
 * @property integer $modsec_requestbody_access_switch
 *
 * @property WebsiteGroup $iWebSiteGroup
 * @property RuleModel $ruleModel
 * @property RuleModel $selfRuleModel
 */
class WebSite extends BaseModel
{
    public $sendPipe = true, $webSiteServersUpdate = true;

    public static function tableName()
    {
        return 't_website';
    }

    public function rulesSource()
    {
        return [
            [['isproxy', 'iWebSiteGroupId',], 'default', 'value' => 1],
            [['type',], 'default', 'value' => 2],
            [['sGroupName'], function ($attribute, $params) {
                if(!(null === $this->$attribute)) return;
                // 查询出站点组的 ruleModelId
                $WebsiteGroupModel = WebsiteGroup::findOne(1);
                $this->$attribute = $WebsiteGroupModel->groupName;
            }, 'skipOnEmpty' => false],
            [['ruleModelId'], function ($attribute, $params) {
                if(!(null === $this->$attribute)) return;
                // 查询出站点组的 ruleModelId
                $WebsiteGroupModel = WebsiteGroup::findOne(1);
                $this->$attribute = $WebsiteGroupModel->ruleModelId;
            }, 'skipOnEmpty' => false],
            [['iWebSitePort', 'iWebSiteGroupId', 'ruleModelId', 'selfRuleModelId', 'modelingperiod', 'mstatus', 'studyTime', 'isproxy', 'type', 'cache', 'helthcheck', 'modsec_requestbody_access_switch'], 'integer'],
            [['modelingstartdate', 'modelingendday', 'beginTime', 'endTime'], 'safe'],
            [['sGroupName', 'sWebSiteName', 'remarks', 'ssl_path1', 'ssl_path2', 'porxy_remark'], 'string', 'max' => 255],
            [['sWebSiteIP'], 'string', 'max' => 64],
            [['iWebSitePort'], 'integer', 'min'=>1, 'max'=>65535],
            [['sWebSiteName', 'iWebSiteGroupId'],'required'],
            /*[['sWebSiteName'], function ($attribute, $params) {
                $val = $this->$attribute;
                $urlValidator = new \yii\validators\UrlValidator();
                $ipValidator = new \yii\validators\IpValidator();
                $errorInfo = Yii::$app->sysLanguage->getTranslateBySymbol('hostHeadName')
                    .Yii::$app->sysLanguage->getTranslateBySymbol('parameterError');
                if ($urlValidator->defaultScheme = 'http' && $urlValidator->validate($val, $error)) return;
                elseif($urlValidator->defaultScheme = 'https' && $urlValidator->validate($val, $error)) return;
                elseif((!$ipValidator->ipv6 = false) && $ipValidator->validate($val, $error)) return;
                else $this->addError($attribute, $errorInfo);
            }],*/
            [['ssl_path1', 'ssl_path2'], function ($attribute, $params) {
                if('https' != $this->sWebSiteProtocol) return;
                $errorInfo = Yii::$app->sysLanguage->getTranslateBySymbol('unabletoObtainUploadFileInformation');
                #检测两个文件都要同时上传
                $sym = $this->getSslPathUploadStatus($params);#0 全都上传,1 上传部分, 2 无上传
                if(1 == $sym) $this->addError($attribute, $errorInfo);#如果有文件上传 必须所有文件同时上传
                if(!(null === $this->id) && 2 == $sym) return;#如果为更新而无上传则跳过
                #保存文件和属性
                if(0 != $_FILES['UploadSingleFile']['error'][$attribute]) $this->addError($attribute, $errorInfo);
                $this->$attribute = Yii::$app->sysPath->cachePath."bd_{$attribute}";
                $model = new \app\logic\model\UploadSingleFile([
                    'key' => $attribute,
                    'path' => $this->$attribute,
                    'rule' => ['maxSize'=>3 * 1024*1024],
                    ]);
                if(!$model->instanceSave())
                    Yii::$app->sysJsonMsg->msg(null, $model->getErrorsInfoString());
            }, 'skipOnEmpty' => false, 'params' => ['ssl_path1', 'ssl_path2'], ],
            [['sWebSiteName', 'iWebSitePort'], 'unique', 'targetAttribute' => ['sWebSiteName', 'iWebSitePort']],
            [['sWebSiteProtocol'], 'string', 'max' => 10],
            [['sWebSiteProtocol'], 'in', 'range' => ['http', 'https']],
            [['daymaxtraffic', 'dayipmaxvisit'], 'string', 'max' => 1024],
            [['ddosfencetype'], 'string', 'max' => 8],
            [['hatype'], 'string', 'max' => 30],
            [['hatype'], 'in', 'range' => ['rotate', 'weight', 'hash']],
            [['modsec_status'], 'string', 'max' => 16],
            [['iWebSiteGroupId'], 'exist', 'skipOnError' => true, 'targetClass' => WebsiteGroup::className(), 'targetAttribute' => ['iWebSiteGroupId' => 'id']],
            [['ruleModelId'], 'exist', 'skipOnError' => true, 'targetClass' => RuleModel::className(), 'targetAttribute' => ['ruleModelId' => 'id']],
            [['selfRuleModelId'], 'exist', 'skipOnError' => true, 'targetClass' => RuleModel::className(), 'targetAttribute' => ['selfRuleModelId' => 'id']],
        ];
    }

    #ssl_path上传文件完整性检测
    private function getSslPathUploadStatus($params){
        $sym = 0;#0 全都上传,1 上传部分, 2 无上传
        foreach ($params as $item){
            if(0 != $_FILES['UploadSingleFile']['error'][$item]) $sym++;
        }
        return $sym;
    }

    #验证代理IP及权重
    public function beforeValidate()
    {
        if(!$this->webSiteServersUpdate) return parent::beforeValidate();
        #验证代理IP及权重
        $WebSite = Yii::$app->request->post('WebSite');
        // 代理IP及端口
        $WebSiteServers = $WebSite['WebSiteServers'];
        if(empty($WebSiteServers))
            Yii::$app->sysJsonMsg->msg(null, Yii::$app->sysLanguage->getTranslateBySymbol('proxyIpAndPortCanNotBeNull'));

        $weight= 0; // 设置一个默认的权重，再判断所有权重设置是否一样
        foreach( $WebSiteServers as $v )
        {
            $ServersArr = explode(':', $v);
            if( Yii::$app->wafHelper->CheckIPV4($ServersArr[0])== false )
                Yii::$app->sysJsonMsg->msg(null, Yii::$app->sysLanguage->getTranslateBySymbol('proxyIpError'));//'代理IP不正确';
            if( intval($ServersArr[1])<1 || intval($ServersArr[1])>65535 )
                Yii::$app->sysJsonMsg->msg(null, Yii::$app->sysLanguage->getTranslateBySymbol('proxyPortError'));//'代理端口错误';
            if( intval($ServersArr[2])<1 || intval($ServersArr[2])>10 )
                Yii::$app->sysJsonMsg->msg(null, Yii::$app->sysLanguage->getTranslateBySymbol('proxyWeightError'));//'代理权重错误';
        }
        return parent::beforeValidate();
    }

    public function afterSave($insert, $changedAttributes)
    {
        if($this->webSiteServersUpdate){
            #删除所有代理相关记录
            WebSiteServers::deleteAll(['webSiteId' => $this->id]);
            #重新加入代理相关记录
            $WebSite = Yii::$app->request->post('WebSite');
            $WebSiteServers = $WebSite['WebSiteServers'];
            foreach( $WebSiteServers as $v )
            {
                $ipPort = explode(':', $v);
                $WebSiteServersModel = new WebSiteServers();
                $WebSiteServersModel->webSiteId = $this->id;
                $WebSiteServersModel->ip = $ipPort[0];
                $WebSiteServersModel->port = $ipPort[1];
                $WebSiteServersModel->weight = $ipPort[2];
                $WebSiteServersModel->protocol = strtoupper($this->sWebSiteProtocol);
                $WebSiteServersModel->type = 2;
                $WebSiteServersModel->save();
            }

            #如果是 https就发出管道并且有文件上传
            if("https" === $this->sWebSiteProtocol  && 0 == $this->getSslPathUploadStatus(['ssl_path1', 'ssl_path2']) )
                Yii::$app->wafHelper->pipe("CMD_SSL_LICENCE|{$this->sWebSiteName}|{$this->ssl_path1}|{$this->ssl_path2}");
        }


        if($this->sendPipe){
            Yii::$app->wafHelper->pipe('CMD_PORT');
            Yii::$app->wafHelper->pipe('CMD_DDOS');
            Yii::$app->wafHelper->pipe('CMD_NGINX');
        }
        parent::afterSave($insert, $changedAttributes);
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'sGroupName' => '站点组名称',
            'sWebSiteName' => '站点名称',
            'sWebSiteIP' => '站点IP',
            'iWebSitePort' => '站点端口',
            'sWebSiteProtocol' => '协议',
            'ssl_path1' => '证书公钥',
            'ssl_path2' => '证书密钥',

            'iWebSiteGroupId' => '站点组ID',
            'ruleModelId' => '策略模板ID',
            'selfRuleModelId' => '自身策略模板ID',
            'daymaxtraffic' => '24小时每小时最大流量模型',
            'dayipmaxvisit' => '24小时每小时单ip最大访问数',
            'modelingstartdate' => '24小时建模开始日期',
            'modelingperiod' => '建模的时间周期',
            'modelingendday' => '建模结束时间',
            'mstatus' => '建模状态',
            'studyTime' => '学习时间',
            'beginTime' => '学习开始时间',
            'endTime' => '学习结束时间',
            'remarks' => '动态建模备注',
            'isproxy' => '是否是反向代理',
            'ddosfencetype' => 'DDOS攻击防护类型',
            'hatype' => '负载均衡方式',
            'type' => '类型',
            'cache' => '开启缓存',
            'helthcheck' => '启用健康检查',
            'porxy_remark' => '反向代理说明',
            'modsec_status' => 'Modsec Status',
            'modsec_requestbody_access_switch' => 'Modsec Requestbody Access Switch',

            'headTitle1' => '<span class="red">*</span>'.
                    Yii::$app->sysLanguage->getTranslateBySymbol('proxyIpAndPort').':('.
                    Yii::$app->sysLanguage->getTranslateBySymbol('proxyWeightValueScopeTips').')',
            'customHtml1' => '',
        ];
    }

    public function getWebSiteServers(){
        $arr = WebSiteServers::find()->where(['webSiteId' => $this->id])->asArray()->all();
        $servers = [];
        foreach ($arr as $v)
            $servers[] = $v['ip'].':'.$v['port'].':'.$v['weight'];
        return join('|', $servers);
    }

    public function returnHatype($type){
        $arr = [
            'rotate' => Yii::$app->sysLanguage->getTranslateBySymbol('polling'),
            'weight' => Yii::$app->sysLanguage->getTranslateBySymbol('weight'),
            'hash' => Yii::$app->sysLanguage->getTranslateBySymbol('ipHash'),
        ];
        return AdminListConfig::returnSelect($type, $arr);
    }

    public function returnWebSiteProtocol($type){
        $arr = ['http' => 'http', 'https' => 'https'];
        return AdminListConfig::returnSelect($type, $arr);
    }

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => ['sWebSiteName', ['isproxy' => 1]],
        ]);
        return ['query' => $query];
    }

    public function ListSearch()
    {
        return [
            'field' => ['sWebSiteName',],
            'key' => $this->modelName,
            'model' => $this,
        ];
    }

    public function ListTable()
    {
        return [
            'field' => [
                'sWebSiteName',
                'sWebSiteProtocol',
                'hatype' => ['type' => 'switch', 'val' => $this->returnHatype('switch')],
                'cache' => ['type' => 'callback', 'val' => function($obj, $val){
                    $class = (1 == $val) ? 'bt_qyan' : 'bt_tyan';
                    $str =  (1 == $val) ? 'enable' : 'stopUse';
                    $status = 1 == $val ? 0 : 1;
                    $str = Yii::$app->sysLanguage->getTranslateBySymbol($str);
                    return "<input type=button class='qt {$class}' onclick='statusChange({$obj['id']}, {$status});' title='{$str}'>";
                }],
                'iWebSitePort',
                'webSiteServers' => ['colName' => Yii::$app->sysLanguage->getTranslateBySymbol('proxyIpAndPort'),],
            ],
            'model' => $this,
            'customStr' => \Yii::$app->view->renderFile('@app/views/rule-custom-defend-policy/list-component.php').
                \Yii::$app->view->renderFile('@app/views/proxy/html.php'),
        ];
    }

    public function ListField()
    {
        $type = AdminListConfig::ListFieldScenarios('common', $this);
        $fieldKey = $this->modelName;

        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'id' => ['showType' => 'hidden'],
                'sWebSiteName' => ['tipsPs' => '*'.Yii::$app->sysLanguage->getTranslateBySymbol('hostNameMustBeIpV4OrDomain').','.
                        Yii::$app->sysLanguage->getTranslateBySymbol('suchAs').'：www.example.com'],
                'sWebSiteProtocol' => array_merge(
                    $this->returnWebSiteProtocol('select'),
                    ['inputProperty' => 'onchange="showSslPath(this)"']
                ),
                'hatype' => $this->returnHatype('select'),
                'cache' => SelectList::enable('radio'),
                'ssl_path1' => ['type' => 'fileWithVal'],
                'ssl_path2' => ['type' => 'fileWithVal'],
                'customHtml1' => ['render' => function($model){
                    return \Yii::$app->view->renderFile('@app/views/proxy/web-site-servers.php', [
                        'model' => $model,
                        // 查询出站点的 代理IP及端口
                        'webSiteServers' => $model->id ? WebSiteServers::find()->where(['webSiteId' => $model->id])->asArray()->all() : []
                    ]);
                },],

                'sGroupName' =>  ['showType' => 'notShow'],
                'sWebSiteIP' =>  ['showType' => 'notShow'],
                'iWebSiteGroupId' =>  ['showType' => 'notShow'],
                'ruleModelId' =>  ['showType' => 'notShow'],
                'selfRuleModelId' =>  ['showType' => 'notShow'],
                'daymaxtraffic' =>  ['showType' => 'notShow'],
                'dayipmaxvisit' =>  ['showType' => 'notShow'],
                'modelingstartdate' =>  ['showType' => 'notShow'],
                'modelingperiod' =>  ['showType' => 'notShow'],
                'modelingendday' =>  ['showType' => 'notShow'],
                'mstatus' =>  ['showType' => 'notShow'],
                'studyTime' =>  ['showType' => 'notShow'],
                'beginTime' =>  ['showType' => 'notShow'],
                'endTime' =>  ['showType' => 'notShow'],
                'remarks' =>  ['showType' => 'notShow'],
                'isproxy' =>  ['showType' => 'notShow'],
                'ddosfencetype' =>  ['showType' => 'notShow'],
                'type' =>  ['showType' => 'notShow'],
                'helthcheck' =>  ['showType' => 'notShow'],
                'modsec_status' =>  ['showType' => 'notShow'],
                'modsec_requestbody_access_switch' =>  ['showType' => 'notShow'],
            ],
            'customStr' => \Yii::$app->view->renderFile('@app/views/proxy/edit-component.php'),
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

    public function getIWebSiteGroup()
    {
        return $this->hasOne(WebsiteGroup::className(), ['id' => 'iWebSiteGroupId']);
    }

    public function getRuleModel()
    {
        return $this->hasOne(RuleModel::className(), ['id' => 'ruleModelId']);
    }

    public function getSelfRuleModel()
    {
        return $this->hasOne(RuleModel::className(), ['id' => 'selfRuleModelId']);
    }

    //获取详情
    public static function getDetail(){
        $id = Yii::$app->request->post('id');
        $model =  WebSite::find()->where(['id'=>$id])->asArray()->one();

        $data['porxy_remark'] = strlen($model['porxy_remark'])>0?$model['porxy_remark']:''; // 备注
        $data['ssl_path1'] = strlen($model['ssl_path1'])>0?$model['ssl_path1']:''; //证书公钥
        $data['ssl_path2'] = strlen($model['ssl_path2'])>0?$model['ssl_path2']:''; //证书密钥
        return json_encode($data);
    }

    //更新状态
    public static function updateStatus(){
        $model = new self;
        $query = Yii::$app->request->bodyParams;
        $id = $query['id'];
        $status = $query['status'];
        if(!is_array($id)) return false;
        foreach ($id as $item) {
            if ('' != $item) {
                $obj = $model->findOne($item);
                $obj->sendPipe = false;
                $obj->webSiteServersUpdate = false;
                $obj->cache = $status;
                $obj->save(false);
            }
        }
        Yii::$app->wafHelper->pipe('CMD_PORT');
        Yii::$app->wafHelper->pipe('CMD_DDOS');
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        Yii::$app->sysJsonMsg->msg(true, '', false);
    }

    //软删除
    public static function recordDelete()
    {
        $query = Yii::$app->request->bodyParams;
        $id = $query['id'];
        if(!is_array($id)) return false;
        self::updateAll(['isproxy'=>0], ['id' => $id]);

        Yii::$app->wafHelper->pipe('CMD_PORT');
        Yii::$app->wafHelper->pipe('CMD_DDOS');
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        Yii::$app->sysJsonMsg->msg(true, '', false);
    }
}
