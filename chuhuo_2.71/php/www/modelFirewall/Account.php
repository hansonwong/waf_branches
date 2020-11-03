<?php

namespace app\modelFirewall;

use Yii;

/**
 * This is the model class for table "m_tbaccount".
 *
 * @property integer $iUserId
 * @property string $sLoginAccount
 * @property string $sPasswd
 * @property string $sUerName
 * @property integer $sRole
 * @property integer $iGender
 * @property string $phone
 * @property string $email
 * @property string $address
 * @property integer $iInsertDate
 * @property integer $iUpdateDate
 * @property integer $iStatus
 * @property integer $iOperationUserId
 * @property integer $iOnline
 * @property integer $iUpdatePwd
 * @property integer $usb_key
 * @property string $usb_pin
 */
class Account extends \app\logic\model\BaseModel
{
    public static function tableName()
    {
        return 'm_tbaccount';
    }

    public static function getDb()
    {
        return Yii::$app->get('dbFirewall');
    }

    public function rulesSource()
    {
        return [
            [['sLoginAccount', 'sPasswd', 'sRole'], 'required'],
            [['sRole', 'iGender', 'iInsertDate', 'iUpdateDate', 'iStatus', 'iOperationUserId', 'iOnline', 'iUpdatePwd', 'usb_key'], 'integer'],
            [['sLoginAccount', 'sUerName', 'phone'], 'string', 'max' => 50],
            [['sPasswd'], 'string', 'max' => 32],
            [['email'], 'string', 'max' => 64],
            [['address'], 'string', 'max' => 255],
            [['usb_pin'], 'string', 'max' => 20],
        ];
    }


    public function attributeLabels()
    {
        return [
            'iUserId' => 'I User ID',
            'sLoginAccount' => 'S Login Account',
            'sPasswd' => 'S Passwd',
            'sUerName' => 'S Uer Name',
            'sRole' => 'S Role',
            'iGender' => 'I Gender',
            'phone' => 'Phone',
            'email' => 'Email',
            'address' => 'Address',
            'iInsertDate' => 'I Insert Date',
            'iUpdateDate' => 'I Update Date',
            'iStatus' => 'I Status',
            'iOperationUserId' => 'I Operation User ID',
            'iOnline' => 'I Online',
            'iUpdatePwd' => 'I Update Pwd',
            'usb_key' => 'Usb Key',
            'usb_pin' => 'Usb Pin',
        ];
    }
}
