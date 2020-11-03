<?php

namespace app\modelLogs;

use Yii;

/**
 * This is the model class for table "t_upgrade_logs".
 *
 * @property integer $id
 * @property string $sFileName
 * @property integer $sFileType
 * @property string $sVersion
 * @property integer $iUpdateTime
 * @property string $sUserName
 * @property string $sContent
 * @property integer $iUpdateResult
 */
class UpgradeLogs extends \app\logic\model\BaseModel
{
    public static function tableName()
    {
        return 't_upgrade_logs';
    }

    public function rulesSource()
    {
        return [
            [['sFileType', 'iUpdateTime', 'iUpdateResult'], 'integer'],
            [['sFileName', 'sVersion', 'sUserName', 'sContent'], 'string', 'max' => 255],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'sFileName' => '上传文件名',
            'sFileType' => '上传类型',
            'sVersion' => '版本号',
            'iUpdateTime' => '上传时间',
            'sUserName' => '上传用户',
            'sContent' => '升级说明',
            'iUpdateResult' => '升级结果',
        ];
    }
}