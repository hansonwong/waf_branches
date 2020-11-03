<?php

namespace app\models;

class SysLanguageEnUs extends \app\logic\model\BaseModel
{
    public static function tableName()
    {
        return 'sys_language_en_us';
    }

    public function getCreateTableSql(){
        $table = self::tableName();
        return "CREATE TABLE `{$table}` (
          `id` int(11) NOT NULL COMMENT '主键',
          `title` text COMMENT '标题',
          PRIMARY KEY (`id`),
          CONSTRAINT `id_fk` FOREIGN KEY (`id`) REFERENCES `sys_language_source` (`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;";
    }

    public function rulesSource()
    {
        return [
            [['id'], 'required'],
            [['id'], 'integer'],
            [['title'], 'string'],
            [['id'], 'exist', 'skipOnError' => true, 'targetClass' => SysLanguageSource::className(), 'targetAttribute' => ['id' => 'id']],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'title' => '标题',
        ];
    }

    public function getId0()
    {
        return $this->hasOne(SysLanguageSource::className(), ['id' => 'id']);
    }
}
