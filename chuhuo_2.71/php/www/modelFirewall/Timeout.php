<?php

namespace app\modelFirewall;

use Yii;

/**
 * This is the model class for table "m_tbtimeout".
 *
 * @property integer $id
 * @property integer $iUserId
 * @property string $username
 * @property string $iSessionId
 * @property integer $iSessionTimeout
 * @property string $sIp
 * @property integer $expireTime
 */
class Timeout extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 'm_tbtimeout';
    }

    /**
     * @return \yii\db\Connection the database connection used by this AR class.
     */
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
            [['iUserId', 'iSessionTimeout', 'expireTime'], 'integer'],
            [['username'], 'string', 'max' => 50],
            [['iSessionId'], 'string', 'max' => 40],
            [['sIp'], 'string', 'max' => 128],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabels()
    {
        return [
            'id' => 'ID',
            'iUserId' => 'I User ID',
            'username' => 'Username',
            'iSessionId' => 'I Session ID',
            'iSessionTimeout' => 'I Session Timeout',
            'sIp' => 'S Ip',
            'expireTime' => 'Expire Time',
        ];
    }
}
