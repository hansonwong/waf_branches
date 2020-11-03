<?php

namespace app\modelFirewallLogs;

use Yii;

/**
 * This is the model class for table "m_tbloginlog".
 *
 * @property integer $iloginLogId
 * @property string $iUserId
 * @property integer $iLoginTime
 * @property string $sIp
 * @property integer $sStatus
 * @property string $sContent
 * @property integer $sRole
 */
class LoginLog extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 'm_tbloginlog';
    }

    /**
     * @return \yii\db\Connection the database connection used by this AR class.
     */
    public static function getDb()
    {
        return Yii::$app->get('dbFirewallLog');
    }

    /**
     * @inheritdoc
     */
    public function rules()
    {
        return [
            [['iLoginTime', 'sStatus'], 'required'],
            [['iLoginTime', 'sStatus', 'sRole'], 'integer'],
            [['iUserId'], 'string', 'max' => 50],
            [['sIp'], 'string', 'max' => 64],
            [['sContent'], 'string', 'max' => 255],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabels()
    {
        return [
            'iloginLogId' => 'Ilogin Log ID',
            'iUserId' => 'I User ID',
            'iLoginTime' => 'I Login Time',
            'sIp' => 'S Ip',
            'sStatus' => 'S Status',
            'sContent' => 'S Content',
            'sRole' => 'S Role',
        ];
    }
}
