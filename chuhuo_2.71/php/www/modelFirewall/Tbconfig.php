<?php

namespace app\modelFirewall;

use Yii;
use app\logic\model\BaseModel;
/**
 * This is the model class for table "m_tbconfig".
 *
 * @property integer $id
 * @property string $sName
 * @property string $sValue
 * @property string $sMark
 * @property string $sCommand
 */
class Tbconfig extends BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 'm_tbconfig';
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
            [['sValue', 'sCommand'], 'string'],
            [['sName'], 'string', 'max' => 128],
            [['sMark'], 'string', 'max' => 512],
            [['sName'], 'unique'],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'sName' => '配置项名称',
            'sValue' => '配置项值',
            'sMark' => '备注',
            'sCommand' => '接口命令',
        ];
    }
}
