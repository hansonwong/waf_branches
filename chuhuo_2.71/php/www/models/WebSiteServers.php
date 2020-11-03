<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;
use \yii\helpers\Url;
/**
 * This is the model class for table "t_website_servers".
 *
 * @property integer $id
 * @property string $ip
 * @property string $port
 * @property string $protocol
 * @property string $os
 * @property string $db
 * @property string $webServer
 * @property string $developmentLanguage
 * @property string $remark
 * @property string $createTime
 * @property string $refreshTime
 * @property integer $webSiteId
 * @property integer $type
 * @property integer $weight
 */
class WebSiteServers extends BaseModel
{
    public static function tableName()
    {
        return 't_website_servers';
    }

    public function rulesSource()
    {
        return [
            [['createTime', 'refreshTime'], 'safe'],
            [['createTime'], 'default', 'value' => date('Y-m-d H:i:s')],
            [['refreshTime'], 'filter', 'filter' => function($value){
                return date('Y-m-d H:i:s');
            }],
            [['ip',], 'ip'],
            [['ip', 'port'],'required'],
            [['port'], 'integer', 'min'=>1, 'max'=>65535],
            [['webSiteId', 'type', 'weight'], 'integer'],
            [['ip', 'os', 'db', 'webServer', 'remark'], 'string', 'max' => 255],
            [['port', 'protocol'], 'string', 'max' => 8],
            [['developmentLanguage'], 'string', 'max' => 32],
            ['protocol', 'in', 'range' => ["HTTP", "HTTPS"]],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'webSiteId' => '站点ID',
            'ip' => 'IP地址',
            'port' => '端口',
            'protocol' => '协议',
            'os' => '操作系统',
            'db' => '数据库',
            'webServer' => 'WEB服务器',
            'developmentLanguage' => '开发语言',
            'remark' => '备注',
            'createTime' => '创建时间',
            'refreshTime' => '更新时间',

            'type' => '类型',
            'weight' => '权重',
        ];
    }

    public function afterSave($insert, $changedAttributes)
    {
        parent::afterSave($insert, $changedAttributes);
        if(!$this->writeServersIpToFile())
            Yii::$app->sysJsonMsg->msg(null, Yii::$app->sysLanguage->getTranslateBySymbol('writeFailure'));
        Yii::$app->wafHelper->pipe('CMD_NGINX');
    }

    public static function writeServersIpToFile()
    {
        $model = self::find()->asArray()->all();
        $contents = '';
        foreach( $model as $v )
        {
            $ip = trim($v['ip']);
            if(strlen($ip)<1) continue;
            $contents .= $ip."\n";
        }
        $file = Yii::$app->sysPath->cachePath.'server_ip.conf';
        return Yii::$app->wafHelper->writeFile($contents, $file);
    }

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => [['webSiteId' => \app\logic\common\Url::getQueryParams($_SERVER['HTTP_REFERER'])['id'] ?? '',],],
        ]);
        return ['query' => $query];
    }

    public function getWebSite(){
        return $this->hasOne(WebSiteByGroup::className(), ['id' => 'webSiteId']);
    }

    public function returnWebSite($type){
        $arr = WebSite::find()->asArray()->all();
        $arr = array_column($arr, 'sWebSiteName', 'id');
        return AdminListConfig::returnSelect($type, $arr);
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
                'webSiteId' => ['type' => 'foreignKey', 'val' => 'webSite:sWebSiteName'],
                'ip', 'port', 'protocol', 'os', 'db', 'webServer', 'developmentLanguage', 'remark',
            ],
            'model' => $this,
        ];
    }

    public function returnProtocol($type){
        $arr = ['HTTP' => 'http', 'HTTPS' => 'https'];
        return AdminListConfig::returnSelect($type, $arr);
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
                'protocol' => $this->returnProtocol('select'),
                'webSiteId' => $this->returnWebSite('select'),

                'createTime' => ['showType' => 'notShow'],
                'refreshTime' => ['showType' => 'notShow'],
                'type' => ['showType' => 'notShow'],
                'weight' => ['showType' => 'notShow'],
            ],
            'customStr' => false,
        ];
        switch ($type) {
            case 'create' :
                $this->webSiteId = Yii::$app->request->get('id');
                break;
            case 'update' :
                break;
            default :
                ;
        }
        return $field;
    }
}
