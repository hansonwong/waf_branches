<?php

namespace app\modelLogs;

use Yii;
use app\logic\model\BaseModel;

/**
 * This is the model class for table "t_viruslogs".
 *
 * @property integer $id
 * @property string $downloadPath
 * @property integer $uploadFileID
 * @property string $result
 */
class Viruslogs extends BaseModel
{
    public static function tableName()
    {
        return 't_viruslogs';
    }

    public static function getDb()
    {
        return Yii::$app->get('dbLogs');
    }

    public function rulesSource()
    {
        return [
            [['uploadFileID'], 'integer'],
            [['result'], 'string'],
            [['downloadPath'], 'string', 'max' => 255],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'downloadPath' => '下载路径',
            'uploadFileID' => '上传文件ID',
            'result' => '检测结果',
        ];
    }
}
