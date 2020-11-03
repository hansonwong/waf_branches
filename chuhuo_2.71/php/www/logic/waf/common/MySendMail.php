<?php

namespace app\logic\waf\common;

use Yii;
use app\models\MailSet;

/**
 * 根据“系统->通知配置”的邮件信息，按“报表管理->定时报表”的邮件通知，启用与禁止来发送邮件
 * Class MySendMail
 * @package app\logic\waf\common
 */
class MySendMail
{
    /**
     * 获取发邮件信息
     * @return array|null|\yii\db\ActiveRecord
     */
    public function getMailSet()
    {
        return MailSet::find()->where(['openMail'=>1])->asArray()->one();
    }

    /**
     * 系统邮件发送函数
     * @param string $reportName 报表的名称
     * @param null $attachment 附件列表
     * @return array
     */
    public function sendMail($reportName, $attachment = null)
    {
        $data = ['code'=>false, 'info'=>''];

        $email_config = $this->getMailSet();
        if( empty($email_config) )
        {
            $data['info'] = '通知设置没有配置';
            return $data;
        }

        if( $this->pingAddress($email_config['smtpserver']) === false )
        {
            $data['info'] = '邮件服务器ping不通';
            return $data;
        }

        $email_user = explode("@", $email_config['sender']);
        $subject = $reportName;
        $body = $reportName."\r\n".Yii::$app->sysLanguage->getTranslateBySymbol('date').': '.date('Y-m-d H:i:s');
        $to = $email_config['receiver'];

        $mailer = Yii::$app->mailer;//new yii\swiftmailer\Mailer();
        $mailer->transport=[
            'class' => 'Swift_SmtpTransport',
            'host' => $email_config['smtpserver'],
            'username' => $email_config['sender'],
            'password' => $email_config['password'],
            'port' => $email_config['smtp_port'],  //25 端口号一般都是这个
            ///'encryption' => 'ssl',//    tls | ssl，这里ssl是不行的， 这个不用配置，否则发不出去
        ];
        $mailer->messageConfig=[
            'charset'=>'UTF-8',
            'from'=>[$email_config['sender']=>$email_user[0]]
        ];
        $mail= $mailer->compose();

        if(is_array($attachment)){
            foreach($attachment as $v){
                $mail->attach($v);
            }
        }

        $mail->setSubject($subject);
        $mail->setTextBody($body);
        $mail->setTo($to);
        $mail->send();

        $data['code'] = true;
        $data['info'] = '成功';
        return $data;
    }

    /**
     * 使用PHP检测能否ping通IP或域名
     * @param $address
     * @return boolean
     */
    public function pingAddress($address)
    {
        $status = -1;

        // Linux 服务器下
        exec("/usr/bin/sudo /usr/bin/ping -c 1 {$address}", $outcome, $status);

        if (0 == $status)
        {
            $status = true;
        }
        else
        {
            $status = false;
        }

        return $status;
    }
}