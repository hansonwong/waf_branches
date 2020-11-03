<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\waf\helpers\WafRegexp;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;
use app\modelFirewall\Tbconfig;

class MailSet extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            ['openMail', 'in', 'range' => [0, 1]],
            ['openPhone', 'in', 'range' => [0, 1]],
            [['openMail', 'openPhone'], 'default', 'value' => 0],
            [['smtpPort'], 'integer'],
            [['smtpPort'], 'integer', 'max' => 65535, 'min' => 1],
            [['sender', 'userName', 'password', 'smtpServer', 'receiver'], 'string', 'max' => 45],
            [['sender', 'password', 'smtpServer', 'receiver', 'smtpPort'], 'required'],
            [['sender'], 'email'],
            [['receiver'], 'email'],
            [['receiverPhone'], function($attribute, $params){
                if(1 == $this->openPhone){
                    if(strlen($this->$attribute)<1){
                        $tips = Yii::$app->sysLanguage->getTranslateBySymbol('addresseePhone').','.Yii::$app->sysLanguage->getTranslateBySymbol('parameterError');
                        $this->addError($attribute, $tips);
                    }
                }
            }, 'skipOnEmpty' => false],
            [['smtpServer'], function($attribute, $params){
                $check = function($sender, $smtp){
                    $domain = substr($sender,strripos($sender, '@')+1);
                    if($domain == $smtp) return true;
                    $domain = '.'.$domain;
                    $domainSmtp = substr($smtp, strripos($smtp, $domain));

                    return $domain == $domainSmtp;
                };
                if(!$check($this->sender, $this->$attribute)){
                    $tips = Yii::$app->sysLanguage->getTranslateBySymbol('smtpServerAddr').Yii::$app->sysLanguage->getTranslateBySymbol('error');
                    $this->addError($attribute, $tips);
                }
            }],
            [['receiverPhone'], 'match', 'pattern' => WafRegexp::$mobile, 'message' => Yii::$app->sysLanguage->getTranslateBySymbol('addresseePhone') . Yii::$app->sysLanguage->getTranslateBySymbol('error')], //收件人手机号码错误
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => 'notificationConfig',

            'openMail' => 'enableGatewayEmailFunction',
            'openPhone' => 'enablePhoneAlertFunction',
            'sender' => 'addressorEmail',
            'userName' => 'addressor',
            'password' => 'addressorPwd',
            'smtpServer' => 'smtpServerAddr',
            'smtpPort' => 'smtpServerPort',
            'receiver' => 'addresseeEmail',
            'receiverPhone' => 'addresseePhone',
        ];
    }

    /**
     * 字段修改、添加配置
     * @return array
     */
    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'openMail' => SelectList::enable('radio'),
                'openPhone' => SelectList::enable('radio'),

                'userName' => ['showType' => 'hidden'],

                'sender' => ['tipsTKey' => 'addressorEmailTips'],
                'password' => ['type' => 'password', 'tipsTKey' => 'addressorLoginPwd'],
                'smtpServer' => ['tipsTKey' => 'sendServer'],
                'smtpPort' => ['tipsTKey' => 'sendPort'],
                'receiver' => ['tipsTKey' => 'receptionEmail'],
                'receiverPhone' => ['tipsTKey' => 'receptionAlertPhone'],
            ],
        ];
        return $field;
    }

    public function afterSave()
    {
        $this->fireMailAlert();
    }

    /**
     * 处理 防火墙数据库； 完成后分发管道通知
     * @return array
     */
    private function fireMailAlert()
    {
        $sym = true;

        $sName = "mailAlert";
        $model = Tbconfig::find()->where(['sName'=>$sName])->one();

        $MailSet= Yii::$app->request->post($this->modelName);

        // {"gateway_mail":"on","souce_alert":"on","send_address":"mailfortestt@163.com","password":"11111","receive_address":"liqian@chinabluedon.cn","smtp_address":"smtp.163.com","smtp_port":"80"}
        $sValueArr = [
            'gateway_mail' => isset($MailSet['openMail'])&&$MailSet['openMail']==1?"on":'',
            'souce_alert' => isset($MailSet['openPhone'])&&$MailSet['openPhone']==1?"on":'',
            'send_address' => $MailSet['sender'],
            'password' => $MailSet['password'],
            'receive_address' => $MailSet['receiver'],
            'smtp_address' => $MailSet['smtpserver'],
            'smtp_port' => $MailSet['smtp_port'],
        ];

        // 获取主键ID
        $id = $model['id'];
        $model = Tbconfig::findOne($id);
        $model->sName= $sName;
        $model->sValue= json_encode($sValueArr);
        $model->sMark="邮件报警设置";
        $model->sCommand="CMD_LOG_ALERT";
        if( !$model->save() ) $sym = false;

        $cmd = $model->sCommand . "|" . Yii::$app->wafHelper->fireConvertData($sValueArr);
        Yii::$app->wafHelper->firePipe($cmd);

        return $sym;
    }
}
