<?php

namespace app\modelLogs;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;
use app\logic\common\CvsHelper;
/**
 * This is the model class for table "t_bdblockedlogs".
 *
 * @property integer $id
 * @property integer $logtime
 * @property string $srcip
 * @property string $host
 * @property integer $bdtime
 */
class BdBlockedLogs extends BaseModel
{
    public static function tableName()
    {
        return 't_bdblockedlogs';
    }

    public static function getDb()
    {
        return Yii::$app->get('dbLogs');
    }

    public function rulesSource()
    {
        return [
            [['logtime', 'srcip', 'host'], 'required'],
            [['logtime', 'bdtime'], 'integer'],
            [['srcip'], 'string', 'max' => 15],
            [['host'], 'string', 'max' => 255],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'logtime' => '攻击时间',
            'srcip' => '源IP地址',
            'host' => '目标主机',
            'bdtime' => '阻断持续时间',
        ];
    }

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => ['srcip', 'host',],
            '-time' => ['logtime',],
        ]);
        return ['query' => $query];
    }

    /**
     * 搜索配置
     * @return array
     */
    public function ListSearch()
    {
        return [
            'field' => [
                'logtime' => ['type' => 'betweenDateTime', 'format' => 'yyyy-MM-dd HH:mm:ss'],
                'srcip',
                'host',
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
                'host',
                'bdtime',
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
                    date('Y-m-d H:i:s',$item->logtime),
                    $item->srcip,
                    $item->host,
                    $item->bdtime,
                ];
            }
        }

        #导出所有数据
        $head = [
            'attackTime',#攻击时间
            'sourceIpAddress',#源IP地址
            'destinationHost',#目标主机
            'blockingDuration(unit:sec)',#阻断持续时间（单位：秒）
        ];

        foreach ($head as $k => $v){
            $head[$k] = $translate->getTranslateBySymbol($v);
        }
        $CvsHepler = new CvsHelper();
        $CvsHepler->exportFileName(Yii::$app->sysLanguage->getTranslateBySymbol('smartBlockLog').date('Y-m-d H:i:s'));
        $CvsHepler->exportHead($head);
        $CvsHepler->exportBody($data);
    }
}
