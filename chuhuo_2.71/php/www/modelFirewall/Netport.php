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
class Netport extends BaseModel
{
    public static function tableName()
    {
        return 'm_tbnetport';
    }

    public static function getDb()
    {
        return Yii::$app->get('dbFirewall');
    }

    /**
     * @inheritdoc
     */
    public function rules()
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

    public function attributeLabels()
    {
        return [
            'id' => 'ID',
            'sPortName' => 'S Port Name',
            'sNetMask' => 'S Net Mask',
            'sWorkMode' => 'S Work Mode',
            'iByManagement' => 'I By Management',
            'iAllowPing' => 'I Allow Ping',
            'iAllowTraceRoute' => 'I Allow Trace Route',
            'iAllowFlow' => 'I Allow Flow',
            'iIPV4ConnectionType' => 'I Ipv4 Connection Type',
            'sIPV4Address' => 'S Ipv4 Address',
            'sIPV4NextJump' => 'S Ipv4 Next Jump',
            'iIPV6ConnectionType' => 'I Ipv6 Connection Type',
            'sIPV6Address' => 'S Ipv6 Address',
            'sIPV6NextJump' => 'S Ipv6 Next Jump',
            'iStatus' => 'I Status',
            'exStatus' => 'Ex Status',
            'iMAC' => 'I Mac',
            'sPortMode' => 'S Port Mode',
            'sLan' => 'S Lan',
            'iAllowLog' => 'I Allow Log',
            'iSSH' => 'I Ssh',
            'iWeb' => 'I Web',
        ];
    }
}
