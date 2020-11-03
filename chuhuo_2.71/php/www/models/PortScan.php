<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;
use \yii\helpers\Url;
use app\logic\model\tools\SelectList;

class PortScan extends BaseModel
{
    public static function tableName()
    {
        return 'port_scan';
    }

    public function rulesSource()
    {
        return [
            [['service', 'os'], 'string'],
            [['ip'], 'string', 'max' => 100],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'ip' => 'IP',
            'port' => '端口',
            'portocol' => '协议',
            'service' => '端口/协议',
            'os' => '操作系统',
            'iWebSiteGroupId' => '站点分组',
        ];
    }


    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '~' => ['ip',],
        ]);
        return ['query' => $query];
    }

    public function getIWebSiteGroupId(){
        return '';
    }

    public function ListSearch()
    {
        return [
            'field' => ['ip', 'port', 'portocol'],
            'key' => $this->modelName,
            'model' => $this,
        ];
    }

    public function ListTable()
    {
        $url = Url::to(['config']);
        $config = Yii::$app->sysLanguage->getTranslateBySymbol('config');
        $urlCreate = str_replace('%2F', '/', Url::to(['create-site']));
        return [
            'publicButton' => [
                ['button' => "<button onclick='dataBox(&quot;config&quot;, &quot;{$url}&quot;, &quot;700&quot;, &quot;300&quot;)' class='btn c_b btn_edit'>{$config}</button>", 'authorityPass' => true],
                ['button' => "<span id='scanStatus' style='font-weight:bold;'>loading......</span>", 'authorityPass' => true],
            ],
            'field' => ['ip', 'port', 'portocol', 'os',
                /*'service' => ['type' => 'callback', 'val' => function($obj, $val){
                    $arr = json_decode($val, true);
                    if(0 == count($arr) || !is_array($arr)) return $val;
                    foreach ($arr as $k => $v) return "$k:$v......";
                }],
                'os' => ['type' => 'callback', 'val' => function($obj, $val){
                    $arr = json_decode($val, true);
                    if(0 == count($arr) || !is_array($arr)) return $val;
                    foreach ($arr as $k => $v) return "{$k}......";
                }],*/
            ],
            'recordOperation' => [
                'create-site' => ['title' => Yii::$app->sysLanguage->getTranslateBySymbol('add'), 'class' => 'list-btn', 'type' => 'box', 'url' => "{$urlCreate}&id=%s",],
            ],
            'model' => $this,
            'customStr' => \Yii::$app->view->renderFile('@app/views/port-scan/index.php'),
        ];
    }

    public function ListField()
    {
        $type = AdminListConfig::ListFieldScenarios('common', $this);
        $fieldKey = $this->modelName;

        $websiteGroup = WebsiteGroup::find()->asArray()->all();
        $websiteGroup = array_column($websiteGroup, 'groupName', 'id');

        $field = [
            'fieldKey' => 'WebSite',
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'id' => ['showType' => 'hidden'],
                'portocol' => ['showType' => 'hidden'],
                'service' => ['showType' => 'hidden'],
                'os' => ['showType' => 'hidden'],
                'ip' => ['showType' => 'disable', 'aliase' => 'sWebSiteName',],
                'port' => ['showType' => 'disable', 'aliase' => 'iWebSitePort',],
                'iWebSiteGroupId' => AdminListConfig::returnSelect('select', $websiteGroup),
            ],
            'customStr' => false,
            'submitUrl' => Url::to(['web-site/create', 'op' => 'webSite', 'call' => 'portScan']),
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

    public static function getDetail(){
        $id = Yii::$app->request->post('id');
        $model =  self::findOne($id);
        $arr = [];
        $arr['service'] = json_decode($model->service, true);
        $arr['os'] = json_decode($model->os, true);
        return json_encode($arr);
    }
}
