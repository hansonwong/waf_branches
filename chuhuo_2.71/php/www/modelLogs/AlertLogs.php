<?php

namespace app\modelLogs;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;

/**
 * This is the model class for table "t_alertlogs".
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
class AlertLogs extends BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_alertlogs';
    }

    /**
     * @return null|object|\yii\db\Connection
     * @throws \yii\base\InvalidConfigException
     */
    public static function getDb()
    {
        return Yii::$app->get('dbLogs');
    }

    /**
     * @inheritdoc
     */
    public function rules()
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

    /**
     * @inheritdoc
     */
    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'AuditLogUniqueID' => 'AuditLogUniqueID',
            'LogDateTime' => '攻击时间',
            'CountryCode' => '地理位置',
            'RegionCode' => '地理位置',
            'City' => '地理位置',
            'SourceIP' => '源IP',
            'SourcePort' => '源端口',
            'DestinationIP' => '目标IP',
            'DestinationPort' => '目标端口',
            'Referer' => 'Referer',
            'UserAgent' => 'UserAgent',
            'HttpMethod' => 'HTTP请求方式',
            'Url' => 'Url',
            'HttpProtocol' => '协议',
            'Host' => '目标主机',
            'RequestContentType' => '请求类型',
            'ResponseContentType' => '响应类型',
            'HttpStatusCode' => '请求状态码',
            'GeneralMsg' => 'GeneralMsg',
            'Rulefile' => '规则文件',
            'RuleID' => '规则ID',
            'MatchData' => '匹配内容',
            'Rev' => 'Rev',
            'Msg' => '一般信息',
            'Severity' => '危害等级',
            'Tag' => 'Tag',
            'Status' => '拦截方式',
        ];
    }

    /**
     * 字段修改、添加配置
     * @return array
     */
    public function ListField()
    {
        $type = AdminListConfig::ListFieldScenarios('common', $this);
        $fieldKey = $this->model_name;

        switch ($type) {
            case 'create' :
                $field = [];
                break;
            case 'update' :
                $field = [
                    'fieldKey' => $fieldKey,
                    'field' => $this->attributeLabels(),
                    'fieldType' => [
                        'log_time' => ['type' => 'timepicker', 'timeFormat' => 'yy-mm-dd', 'dateFormat' => 'HH:mm:ss'],
                        'content' => ['type' => 'textarea', 'length' => 0, 'height' => '150px'],
                    ],
                    'customStr' => false,
                ];
                break;
            default :
                ;
        }
        return $field;
    }
}
