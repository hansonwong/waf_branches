<?php

namespace app\modelLogs;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;
use app\logic\common\CvsHelper;

/**
 * This is the model class for table "t_ddoslogs".
 *
 * @property integer $id
 * @property integer $logtime
 * @property string $srcip
 * @property string $CountryCode
 * @property string $RegionCode
 * @property string $City
 * @property string $dstip
 * @property string $dstport
 * @property string $protocol
 * @property string $desc
 */
class DdosLogs extends BaseModel
{
    public static function tableName()
    {
        return 't_ddoslogs';
    }

    public static function getDb()
    {
        return Yii::$app->get('dbLogs');
    }

    public function rulesSource()
    {
        return [
            [['logtime', 'srcip', 'dstip'], 'required'],
            [['logtime'], 'integer'],
            [['srcip', 'dstip'], 'string', 'max' => 15],
            [['CountryCode'], 'string', 'max' => 3],
            [['RegionCode', 'protocol'], 'string', 'max' => 8],
            [['City'], 'string', 'max' => 32],
            [['dstport'], 'string', 'max' => 6],
            [['desc'], 'string', 'max' => 64],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'logtime' => '攻击时间',
            'srcip' => '源IP地址',
            'CountryCode' => '地理位置',
            'RegionCode' => '地理位置',
            'City' => '地理位置',
            'dstip' => '目标IP地址',
            'dstport' => '目标端口',
            'protocol' => '协议',
            'desc' => '描述',
        ];
    }

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => ['srcip', 'dstip', 'dstport', 'protocol'],
            '-time' => ['logtime',],
        ]);
        return ['query' => $query];
    }

    public function ListSearch()
    {
        return [
            'field' => [
                'logtime' => ['type' => 'betweenDateTime', 'format' => 'yyyy-MM-dd HH:mm:ss'],
                'srcip',
                'dstip',
                'dstport',
                'protocol',
            ],
            'key' => $this->modelName,
            'model' => $this,
        ];
    }

    public function ListTable()
    {
        return [
            'field' => [
                'logtime' => ['type' => 'custom', 'valType' => 'datetime'],
                'srcip',
                'City' => ['type' => 'callback', 'val' => function($obj, $val){
                    return \app\logic\waf\helpers\WafModels::getCountry($obj->CountryCode, $obj->RegionCode, $obj->City);
                }],
                'dstip',
                'dstport',
                'protocol',
                'desc',
            ],
            'model' => $this
        ];
    }

    //导出记录
    public static function export(){
        $translate = Yii::$app->sysLanguage;
        $pageSize = 1000;#数据分批获取数量
        $data = [];#所有数据

        #获取分页信息
        $table = new self;#数据模型对象
        $dataProvider = AdminListConfig::getActiveDataProviderSetting(
            array_merge(
                $table->search(Yii::$app->request->post()),
                ['pagesize' => $pageSize, 'page' => 0]
            )
        );
        $pagination = $dataProvider->getPagination();
        $dataProvider->getModels();
        $pageCount = $pagination->getPageCount();
        #获取分页信息END

        #获取所有数据
        for($i = 0; $i < $pageCount; $i++){
            $dataProvider = AdminListConfig::getActiveDataProviderSetting(
                array_merge(
                    $table->search(Yii::$app->request->post()),
                    ['pagesize' => $pageSize, 'page' => $i]
                )
            );
            $dataList = $dataProvider->getModels();

            foreach($dataList as $item){
                $data[] = [
                    date('Y-m-d H:i:s', $item->logtime),
                    $item->srcip,
                    $item->dstip,
                    $item->dstport,
                    $item->protocol,
                    \app\logic\waf\helpers\WafModels::getCountry($item->CountryCode, $item->RegionCode, $item->City),
                    $item->desc,
                ];
            }
        }

        #导出所有数据
        $head = [
            'attackTime',  //攻击时间
            'sourceIpAddress',  //源IP地址
            'targetIpAddress',  //目标IP地址
            'destinationPort',  //目标端口
            'protocol',  //协议
            'geographicalPosition',  //地理位置
            //描述
        ];

        foreach ($head as $k => $v){
            $head[$k] = $translate->getTranslateBySymbol($v);
        }
        $CvsHepler = new CvsHelper();
        $CvsHepler->exportFileName($file = "DDOS".Yii::$app->sysLanguage->getTranslateBySymbol('log').date('Y-m-d H:i:s'));
        $CvsHepler->exportHead($head);
        $CvsHepler->exportBody($data);
    }
}
