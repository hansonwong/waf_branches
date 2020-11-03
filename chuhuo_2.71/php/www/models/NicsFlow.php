<?php

namespace app\models;

use Yii;

/**
 * This is the model class for table "t_nicsflow".
 *
 * @property string $nic
 * @property string $mac
 * @property string $mode
 * @property integer $status
 * @property integer $rcv_pks
 * @property integer $snd_pks
 * @property integer $rcv_bytes
 * @property integer $snd_bytes
 * @property integer $rcv_errs
 * @property integer $snd_errs
 * @property integer $rcv_losts
 * @property integer $snd_losts
 * @property integer $rcv_ratio
 * @property integer $snd_ratio
 * @property integer $time
 */
class NicsFlow extends \app\logic\model\BaseModel
{
    /**
     * @inheritdoc
     */
    public static function tableName()
    {
        return 't_nicsflow';
    }

    /**
     * @inheritdoc
     */
    public function rules()
    {
        return [
            [['nic', 'time'], 'required'],
            [['status', 'rcv_pks', 'snd_pks', 'rcv_bytes', 'snd_bytes', 'rcv_errs', 'snd_errs', 'rcv_losts', 'snd_losts', 'rcv_ratio', 'snd_ratio', 'time'], 'integer'],
            [['nic'], 'string', 'max' => 20],
            [['mac'], 'string', 'max' => 45],
            [['mode'], 'string', 'max' => 4],
        ];
    }

    /**
     * @inheritdoc
     */
    public function attributeLabels()
    {
        return [
            'nic' => Yii::t('app', 'NIC name'),
            'mac' => Yii::t('app', 'mac address'),
            'mode' => Yii::t('app', 'work mode'),
            'status' => Yii::t('app', 'link status'),
            'rcv_pks' => Yii::t('app', 'received packets'),
            'snd_pks' => Yii::t('app', 'sended packets'),
            'rcv_bytes' => Yii::t('app', 'received bytes'),
            'snd_bytes' => Yii::t('app', 'sended bytes'),
            'rcv_errs' => Yii::t('app', 'received error packets'),
            'snd_errs' => Yii::t('app', 'sended error packets'),
            'rcv_losts' => Yii::t('app', 'lost packets when receive'),
            'snd_losts' => Yii::t('app', 'lost packets when sended'),
            'rcv_ratio' => Yii::t('app', 'receive rate'),
            'snd_ratio' => Yii::t('app', 'send rate'),
            'time' => Yii::t('app', 'Time'),
        ];
    }
}
