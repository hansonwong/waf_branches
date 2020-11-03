<?php

namespace app\modelFirewall;

use Yii;
use app\logic\model\BaseModel;

/**
 * This is the model class for table "m_tbbridgedevice".
 *
 * @property integer $id
 * @property string $sBridgeName
 * @property string $sBindDevices
 * @property integer $iByManagement
 * @property integer $iAllowPing
 * @property integer $iAllowTraceRoute
 * @property integer $iAllowLog
 * @property string $sIPV4
 * @property string $sIPV4Mask
 * @property string $sIPV6
 * @property string $sIPV6Mask
 * @property integer $iStatus
 * @property integer $iSSH
 * @property integer $iWeb
 */
class TbBridgeDevice extends BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 'm_tbbridgedevice';
    }

    /**
     * @return null|object|\yii\db\Connection
     * @throws \yii\base\InvalidConfigException
     */
    public static function getDb()
    {
        return Yii::$app->get('dbFirewall');
    }

    /**
     * @inheritdoc
     */
    public function rulesSource()
    {
        return [
            [['iByManagement', 'iAllowPing', 'iAllowTraceRoute', 'iAllowLog', 'iStatus', 'iSSH', 'iWeb'], 'integer'],
            [['sBridgeName'], 'string', 'max' => 64],
            [['sBindDevices', 'sIPV4', 'sIPV6'], 'string', 'max' => 512],
            [['sIPV4Mask', 'sIPV6Mask'], 'string', 'max' => 32],
            [['bridgeType'], 'string', 'max' => 255],
            ['sBridgeName', 'unique'],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabelsSource()
    {
        return [
            'id' =>  'ID',
            'sBridgeName' => '桥设备名称',
            'sBindDevices' => '绑定设备列表',
            'iByManagement' => '是否用于管理',
            'iAllowPing' => '是否允许ping',
            'iAllowTraceRoute' => '是否允许traceroute',
            'iAllowLog' => '是启用日志',
            'sIPV4' => 'IPV4地址',
            'sIPV4Mask' => 'IPV4掩码',
            'sIPV6' => 'IPV6地址',
            'sIPV6Mask' => 'IPV6掩码',
            'iStatus' => '是否启用',
            'iSSH' => '是否SSH',
            'iWeb' => '是否WEBUI',
            'bridgeType' => '桥的类型',
        ];
    }
}
