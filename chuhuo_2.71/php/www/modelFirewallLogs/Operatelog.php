<?php

namespace app\modelFirewallLogs;

use Yii;

/**
 * This is the model class for table "m_tboperatelog".
 *
 * @property integer $iLogId
 * @property integer $iDateTime
 * @property string $sIp
 * @property string $sOperateUser
 * @property string $sRs
 * @property string $sContent
 * @property string $sOperateAction
 * @property integer $sRole
 */
class Operatelog extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 'm_tboperatelog';
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
            [['iDateTime', 'sIp', 'sOperateUser', 'sRs', 'sContent'], 'required'],
            [['iDateTime', 'sRole'], 'integer'],
            [['sIp'], 'string', 'max' => 64],
            [['sOperateUser'], 'string', 'max' => 50],
            [['sRs', 'sOperateAction'], 'string', 'max' => 200],
            [['sContent'], 'string', 'max' => 255],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabels()
    {
        return [
            'iLogId' => 'I Log ID',
            'iDateTime' => 'I Date Time',
            'sIp' => 'S Ip',
            'sOperateUser' => 'S Operate User',
            'sRs' => 'S Rs',
            'sContent' => 'S Content',
            'sOperateAction' => 'S Operate Action',
            'sRole' => 'S Role',
        ];
    }
}
