<?php

namespace app\models;

use Yii;

/**
 * This is the model class for table "t_migrate".
 *
 * @property integer $id
 * @property string $sVersion
 * @property string $sVersionNum
 * @property string $sOldVersionNum
 * @property string $sAction
 * @property string $sTime
 * @property string $sDesc
 * @property string $sMark
 * @property integer $iStatus
 */
class Migrate extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_migrate';
    }

    /**
     * @inheritdoc
     */
    public function rulesSource()
    {
        return [
            [['sMark'], 'required'],
            [['sMark'], 'string'],
            [['iStatus'], 'integer'],
            [['sVersion', 'sAction', 'sTime', 'sDesc'], 'string', 'max' => 255],
            [['sVersionNum', 'sOldVersionNum'], 'string', 'max' => 32],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'sVersion' => '版本号',
            'sVersionNum' => '项目版本号',
            'sOldVersionNum' => '上一版本号',
            'sAction' => '操作',
            'sTime' => '时间',
            'sDesc' => '描述',
            'sMark' => '备注',
            'iStatus' => '状态',
        ];
    }
}
