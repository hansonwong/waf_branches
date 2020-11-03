<?php

namespace app\modelFirewall;

use Yii;
use app\logic\model\BaseModel;
/**
 * This is the model class for table "m_tbnetport".
 *
 * @property integer $id
 * @property string $sPortName
 * @property string $sNetMask
 * @property string $sWorkMode
 * @property integer $iByManagement
 * @property integer $iAllowPing
 * @property integer $iAllowTraceRoute
 * @property integer $iAllowFlow
 * @property integer $iIPV4ConnectionType
 * @property string $sIPV4Address
 * @property string $sIPV4NextJump
 * @property integer $iIPV6ConnectionType
 * @property string $sIPV6Address
 * @property string $sIPV6NextJump
 * @property string $iStatus
 * @property integer $exStatus
 * @property string $iMAC
 * @property integer $sPortMode
 * @property string $sLan
 * @property integer $iAllowLog
 * @property integer $iSSH
 * @property integer $iWeb
 */
class TbNetPort extends BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 'm_tbnetport';
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
            [['iByManagement', 'iAllowPing', 'iAllowTraceRoute', 'iAllowFlow', 'iIPV4ConnectionType', 'iIPV6ConnectionType', 'exStatus', 'sPortMode', 'iAllowLog', 'iSSH', 'iWeb'], 'integer'],
            [['sIPV4Address', 'sIPV6Address'], 'string'],
            [['sPortName'], 'string', 'max' => 128],
            [['sNetMask', 'sWorkMode'], 'string', 'max' => 64],
            [['sIPV4NextJump', 'sIPV6NextJump'], 'string', 'max' => 32],
            [['iStatus'], 'string', 'max' => 11],
            [['iMAC', 'sLan'], 'string', 'max' => 100],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabels()
    {
        return [
            'id' => 'ID',
            'sPortName' => '接口名称',
            'sNetMask' => '子网掩码',
            'sWorkMode' => '工作模式', //'工作模式route:路由模式bridge:桥模式 virtual：虚拟线 bypass：旁路模式 nat：NAT模式  mirror：镜像模式 redundancy：冗余模式'),
            'iByManagement' => '是否用于管理',
            'iAllowPing' => '是否允许ping',
            'iAllowTraceRoute' => '是否允许traceroute',
            'iAllowFlow' => '允许流控',
            'iIPV4ConnectionType' => 'ipv4连接类型',
            'sIPV4Address' => 'ipv4地址',
            'sIPV4NextJump' => 'ipv4下一跳',
            'iIPV6ConnectionType' => 'ipv6连接类型',
            'sIPV6Address' => 'ipv6地址',
            'sIPV6NextJump' => 'ipv6下一跳',
            'iStatus' => '是否启动',
            'exStatus' =>'例外网口',
            'iMAC' => 'iMac',
            'sPortMode' => '网口模式',
            'sLan' => 'vEth口对应的lan口',
            'iAllowLog' => '运行日志',
            'iSSH' => '是否SSH',
            'iWeb' => '是否WEBUI',
        ];
    }
}
