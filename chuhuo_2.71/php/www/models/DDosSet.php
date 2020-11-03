<?php

namespace app\models;

use Yii;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;

class DDosSet extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['bankWidth', 'totalPacket', 'perPacket', 'tcpPacket', 'perTcpPacket', 'synPacket', 'perSynPacket', 'ackPacket', 'perAckPacket', 'otherTcp', 'perOtherTcp', 'udpPacket', 'perUdpPacket', 'icmpPacket', 'perIcmpPacket', 'ddosEnable', 'udpEnable', 'icmpEnable'], 'integer'],
            [['bankWidth'], 'integer', 'max' => 1024, 'min' => 1],
            [['totalPacket', 'perPacket', 'tcpPacket', 'perTcpPacket', 'synPacket', 'perSynPacket', 'ackPacket', 'perAckPacket', 'otherTcp', 'perOtherTcp', 'udpPacket', 'perUdpPacket', 'icmpPacket', 'perIcmpPacket'], 'integer', 'max' => 10000, 'min' => 1],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => 'dDosDefendConfig',
            'ddosEnable' => '开启DDOS云防护',

            'bankWidth' => '网络流量',
            'totalPacket' => '总流量触发阀值',
            'perPacket' => '总流量阀值/单IP',

            'tcpPacket' => 'TCP 包触发阀值',
            'perTcpPacket' => 'TCP 包阀值/单IP',
            'otherTcp' => '其它TCP Flood触发阀值',
            'perOtherTcp' => '其它TCP Flood阀值/单IP',

            'synPacket' => 'SYN Flood触发阀值',
            'perSynPacket' => 'SYN Flood阀值/单IP',

            'ackPacket' => 'ACK Flood 数据包/秒',
            'perAckPacket' => 'ACK Flood 包阀值/单IP',

            'udpEnable' => 'UDP 禁止',
            'udpPacket' => 'UDP 数据包/秒',
            'perUdpPacket' => 'UDP 包阀值/单IP',

            'icmpEnable' => 'ICMP 禁止',
            'icmpPacket' => 'ICMP 数据包/秒',
            'perIcmpPacket' => 'ICMP 包阀值/单IP',
        ];
    }

    public function ListField()
    {
        $numTips = Yii::$app->sysLanguage->getTranslateBySymbol('dataPackage/second').'(1-10000)';
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'ddosEnable' => SelectList::enable('radio'),
                'udpEnable' => array_merge(SelectList::enable('radio'), ['tipsPsTKey' => ['allUdpProtocolCommunicationDisableTips']]),
                'icmpEnable' => array_merge(SelectList::enable('radio'), ['tipsPsTKey' => ['allIcmpProtocolCommunicationDisableTips']]),

                'bankWidth' => ['tips' => 'Mbps(1-1024) '.Yii::$app->sysLanguage->getTranslateBySymbol('recommendThresholdTips')],

                'totalPacket' => ['tips' => $numTips],
                'perPacket' => ['tips' => $numTips],

                'tcpPacket' => ['tips' => $numTips],
                'perTcpPacket' => ['tips' => $numTips],
                'otherTcp' => ['tips' => $numTips],
                'perOtherTcp' => ['tips' => $numTips],

                'synPacket' => ['tips' => $numTips],
                'perSynPacket' => ['tips' => $numTips],

                'ackPacket' => ['tips' => $numTips],
                'perAckPacket' => ['tips' => $numTips],

                'udpPacket' => ['tips' => $numTips],
                'perUdpPacket' => ['tips' => $numTips],

                'icmpPacket' => ['tips' => $numTips],
                'perIcmpPacket' => ['tips' => $numTips],
            ],
            'button' => [
                'submit' => [
                    ['text' => Yii::$app->sysLanguage->getTranslateBySymbol('recommendThreshold'), 'attrs' => 'onclick="setRecommendValue();"'],
                    ['text' => Yii::$app->sysLanguage->getTranslateBySymbol('reset'), 'attrs' => 'onclick="resetValue();"'],
                ],
            ],
            'customStr' => \Yii::$app->view->renderFile('@app/views/d-dos-set/config.php'),
        ];
        return $field;
    }

    public function save(){
        $result = parent::save();
        Yii::$app->wafHelper->pipe('CMD_DDOS');
        return $result;
    }
}
