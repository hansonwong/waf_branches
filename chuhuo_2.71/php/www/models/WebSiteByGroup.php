<?php

namespace app\models;

use Yii;
use app\logic\model\BaseModel;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;
use \yii\helpers\Url;
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
class WebSiteByGroup extends BaseModel
{
    public static function tableName()
    {
        return 't_website';
    }

    public function rulesSource()
    {
        return [
            [['sWebSiteName', 'iWebSiteGroupId'],'required'],
            [['iWebSiteGroupId'], function ($attribute, $params) {
                $websiteGroup = WebsiteGroup::findOne($this->$attribute);
                $this->ruleModelId = $websiteGroup->ruleModelId;
                $this->sGroupName = $websiteGroup->groupName;
            }],
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
            [['iWebSitePort'], 'integer', 'min'=>1, 'max'=>65535],
            [['iWebSitePort', 'iWebSiteGroupId', 'ruleModelId', 'selfRuleModelId', 'modelingperiod', 'mstatus', 'studyTime', 'isproxy', 'type', 'cache', 'helthcheck', 'modsec_requestbody_access_switch'], 'integer'],
            [['modelingstartdate', 'modelingendday', 'beginTime', 'endTime'], 'safe'],
            [['sGroupName', 'sWebSiteName', 'remarks', 'ssl_path1', 'ssl_path2', 'porxy_remark'], 'string', 'max' => 255],
            [['sWebSiteIP'], 'string', 'max' => 64],
            [['sWebSiteProtocol'], 'string', 'max' => 10],
            [['daymaxtraffic', 'dayipmaxvisit'], 'string', 'max' => 1024],
            [['ddosfencetype'], 'string', 'max' => 8],
            [['hatype'], 'string', 'max' => 30],
            [['modsec_status'], 'string', 'max' => 16],
            [['sWebSiteName', 'iWebSitePort'], 'unique', 'targetAttribute' => ['sWebSiteName', 'iWebSitePort'], 'message' => 'The combination of S Web Site Name and I Web Site Port has already been taken.'],
            [['iWebSiteGroupId'], 'exist', 'skipOnError' => true, 'targetClass' => WebsiteGroup::className(), 'targetAttribute' => ['iWebSiteGroupId' => 'id']],
            [['ruleModelId'], 'exist', 'skipOnError' => true, 'targetClass' => RuleModel::className(), 'targetAttribute' => ['ruleModelId' => 'id']],
            [['selfRuleModelId'], 'exist', 'skipOnError' => true, 'targetClass' => RuleModel::className(), 'targetAttribute' => ['selfRuleModelId' => 'id']],
        ];
    }

    public function afterSave($insert, $changedAttributes)
    {
        parent::afterSave($insert, $changedAttributes);
        $selfRuleModelId = $changedAttributes['selfRuleModelId'] ?? 0;
        if(!$insert && $this->selfRuleModelId != $selfRuleModelId){
            // 更新RuleModel表
            RuleModel::updateAll(['ischecked'=>1], ['id' => $this->selfRuleModelId]);
            RuleModel::updateAll(['ischecked'=>0], ['id' => $selfRuleModelId]);
        }
        Yii::$app->wafHelper->pipe('CMD_NGINX');
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

    public function returnIWebSiteGroupId($type){
        $arr = WebsiteGroup::find()->asArray()->all();
        $arr = array_column($arr, 'groupName', 'id');
        return AdminListConfig::returnSelect($type, $arr);
    }

    public function returnRuleModelId($type){
        $websiteGroup = WebsiteGroup::findOne($this->iWebSiteGroupId);
        $arr = RuleModel::find()->select(['id','name'])->where(['type' => 2, 'groupModelId' => $websiteGroup->ruleModelId])->asArray()->all();
        $arr = array_column($arr, 'name', 'id');
        return AdminListConfig::returnSelect($type, $arr);
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
            'isproxy' => '是否反向代理',
            'ddosfencetype' => 'DDOS攻击防护类型',
            'hatype' => '负载均衡方式',
            'type' => '类型',
            'cache' => '开启缓存',
            'helthcheck' => '启用健康检查',
            'porxy_remark' => '反向代理说明',
            'modsec_status' => 'Modsec Status',
            'modsec_requestbody_access_switch' => 'Modsec Requestbody Access Switch',
        ];
    }

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => [['iWebSiteGroupId' => \app\logic\common\Url::getQueryParams($_SERVER['HTTP_REFERER'])['id'] ?? '',],],
        ]);
        return ['query' => $query];
    }

    public function ListTable()
    {
        $createButtonText = Yii::$app->sysLanguage->getTranslateBySymbol('add');
        $url = Url::to(['create', 'id' => Yii::$app->request->get('id')]);
        return [
            'publicButton' => [
                'create' => "<button id='data_add' onclick=\"dataBox('{$createButtonText}','{$url}', 500, 400)\" class='btn c_g btn_add'>{$createButtonText}</button>",
            ],
            'field' => [
                'iWebSiteGroupId' => ['type' => 'foreignKey', 'val' => 'iWebSiteGroup:groupName'],
                'sWebSiteName',
                'iWebSitePort',
                'ruleModelId' => ['type' => 'foreignKey', 'val' => 'ruleModel:name'],
                'selfRuleModelId' => ['type' => 'foreignKey', 'val' => 'selfRuleModel:name'],
                'isproxy' => ['float' => 'c', 'type' => 'switch', 'val' => SelectList::enable('switch')],
            ],
            'model' => $this,
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
                #'sWebSiteName' => ['showType' => 'notShow'],
                'iWebSiteGroupId' => $this->returnIWebSiteGroupId('select'),

                'sWebSiteProtocol' => ['showType' => 'notShow'],
                'selfRuleModelId' => ['showType' => 'notShow'],
                'porxy_remark' => ['showType' => 'notShow'],
                'hatype' => ['showType' => 'notShow'],
                'cache' => ['showType' => 'notShow'],
                'ssl_path1' => ['showType' => 'notShow'],
                'ssl_path2' => ['showType' => 'notShow'],

                'sGroupName' => ['showType' => 'notShow'],
                'sWebSiteIP' => ['showType' => 'notShow'],

                'ruleModelId' => ['showType' => 'notShow'],
                'daymaxtraffic' => ['showType' => 'notShow'],
                'dayipmaxvisit' => ['showType' => 'notShow'],
                'modelingstartdate' => ['showType' => 'notShow'],
                'modelingperiod' => ['showType' => 'notShow'],
                'modelingendday' => ['showType' => 'notShow'],
                'mstatus' => ['showType' => 'notShow'],
                'studyTime' => ['showType' => 'notShow'],
                'beginTime' => ['showType' => 'notShow'],
                'endTime' => ['showType' => 'notShow'],
                'remarks' => ['showType' => 'notShow'],
                'isproxy' => ['showType' => 'notShow'],
                'ddosfencetype' => ['showType' => 'notShow'],
                'type' => ['showType' => 'notShow'],
                'helthcheck' => ['showType' => 'notShow'],
                'modsec_status' => ['showType' => 'notShow'],
                'modsec_requestbody_access_switch' =>  ['showType' => 'notShow'],
            ],
            'customStr' => \Yii::$app->view->renderFile('@app/views/proxy/edit-component.php'),
        ];
        switch ($type) {
            case 'create' :
                $this->iWebSiteGroupId = Yii::$app->request->get('id');
                break;
            case 'update' :
                $field['fieldType']['selfRuleModelId'] = $this->returnRuleModelId('select');
                break;
            default :
                ;
        }
        return $field;
    }

    public static function checkBeforeDelete($idArr){
        $count = WebSite::find()->where(['isproxy' => 1, 'id' => $idArr])->count();
        if(0 < $count) Yii::$app->sysJsonMsg->msg(false, Yii::$app->sysLanguage->getTranslateBySymbol('selectedSiteGroupThereIsReverseProxySite'));
    }
}
