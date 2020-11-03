<?php

namespace app\models;

use Yii;

class SysLanguageSource extends \app\logic\model\BaseModel
{
    public static function tableName()
    {
        return 'sys_language_source';
    }

    public function getCreateTableSql(){
        $table = self::tableName();
        return "CREATE TABLE `{$table}` (
          `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
          `title` char(255) DEFAULT '' COMMENT '标题',
          `is_use` char(1) NOT NULL DEFAULT '1',
          PRIMARY KEY (`id`),
          UNIQUE KEY `uidx_title` (`title`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;";
    }

    public function rulesSource()
    {
        return [
            ['id', 'integer'],
            [['title'], 'string', 'max' => 255],
            [['title'], 'unique'],
            [['is_use'], 'string', 'max' => 1],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'title' => '标题',
            'is_use' => '可用',
        ];
    }

    public function getSysLanguageEnUs()
    {
        return $this->hasOne(SysLanguageEnUs::className(), ['id' => 'id']);
    }
}
