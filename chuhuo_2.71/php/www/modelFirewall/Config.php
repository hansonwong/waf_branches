<?php

namespace app\modelFirewall;

use Yii;

/**
 * This is the model class for table "m_tbconfig".
 *
 * @property integer $id
 * @property string $sName
 * @property string $sValue
 * @property string $sMark
 * @property string $sCommand
 */
class Config extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 'm_tbconfig';
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
            [['sValue', 'sCommand'], 'string'],
            [['sName'], 'string', 'max' => 128],
            [['sMark'], 'string', 'max' => 512],
            [['sName'], 'unique'],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabels()
    {
        return [
            'id' => 'ID',
            'sName' => 'S Name',
            'sValue' => 'S Value',
            'sMark' => 'S Mark',
            'sCommand' => 'S Command',
        ];
    }
}
