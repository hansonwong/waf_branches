<?php

namespace app\models;

use Yii;
use app\logic\model\BaseModel;
/**
 * This is the model class for table "t_license".
 *
 * @property string $sn
 * @property integer $vertype
 * @property integer $validate
 * @property string $company
 * @property string $address
 * @property string $email
 * @property string $telephone
 * @property string $licensefile
 */
class License extends BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_license';
    }

    /**
     * @inheritdoc
     */
    public function rulesSource()
    {
        return [
            [['sn'], 'required'],
            [['vertype', 'validate'], 'integer'],
            [['sn', 'company', 'telephone'], 'string', 'max' => 100],
            [['address', 'licensefile'], 'string', 'max' => 255],
            [['email'], 'string', 'max' => 45],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabelsSource()
    {
        return [
            'sn' => '授权序列号',
            'vertype' => '版本类型',
            'validate' => '有效期',
            'company' => '公司名称',
            'address' => '公司地址',
            'email' => '电子邮箱',
            'telephone' => '联系电话',
            'licensefile' => '许可证文件',
        ];
    }
}
