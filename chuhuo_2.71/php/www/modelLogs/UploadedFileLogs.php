<?php

namespace app\modelLogs;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;
use app\logic\common\CvsHelper;
/**
 * This is the model class for table "t_uploadedfilelogs".
 *
 * @property integer $id
 * @property integer $reporttime
 * @property string $url
 * @property string $filename
 * @property integer $uploadtime
 * @property integer $type
 * @property string $rating
 * @property string $result
 */
class UploadedFileLogs extends BaseModel
{
    public static function tableName()
    {
        return 't_uploadedfilelogs';
    }

    public static function getDb()
    {
        return Yii::$app->get('dbLogs');
    }

    public function rulesSource()
    {
        return [
            [['reporttime', 'uploadtime', 'type'], 'integer'],
            [['result'], 'string'],
            [['url', 'filename'], 'string', 'max' => 64],
            [['rating'], 'string', 'max' => 10],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'reporttime' => '报告时间',
            'url' =>  '站点URL',
            'filename' => '文件名',
            'uploadtime' => '上传时间',
            'type' => '是否病毒',
            'rating' => '严重等级',
            'result' => '检查结果',
        ];
    }

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '~' => ['url', 'filename',],
            '-time' => ['reporttime', 'uploadtime',],
        ]);
        return ['query' => $query];
    }

    public function ListSearch()
    {
        return [
            'field' => [
                'reporttime' => ['type' => 'betweenDateTime', 'format' => 'yyyy-MM-dd HH:mm:ss'],
                'uploadtime' => ['type' => 'betweenDateTime', 'format' => 'yyyy-MM-dd HH:mm:ss'],
                'url',
                'filename',
            ],
            'key' => $this->modelName,
            'model' => $this,
        ];
    }

    public function ListTable()
    {
        return [
            'field' => [
                'reporttime' => ['type' => 'custom', 'valType' => 'datetime'],
                'rating' => ['type' => 'switch', 'val' => AdminListConfig::returnSelect('switch', self::returnRating())],
                'url',
                'filename',
                'uploadtime' => ['type' => 'custom', 'valType' => 'datetime'],
                'type' => ['type' => 'switch', 'val' => AdminListConfig::returnSelect('switch', self::retrunType())],
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

        $rating = self::returnRating();

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
                    date('Y-m-d H:i:s', $item->reporttime),
                    $rating[strtolower($item->rating)],
                    $item->url,
                    $item->filename,
                    date('Y-m-d H:i:s', $item->uploadtime),
                ];
            }
        }

        #导出所有数据
        $head = [
            'reportingTime',#报告时间
            'severityLevel',#严重等级
            'siteUrl',#站点URL
            'fileName',#文件名
            'uploadTime',#上传时间
        ];

        foreach ($head as $k => $v){
            $head[$k] = $translate->getTranslateBySymbol($v);
        }
        $CvsHepler = new CvsHelper();
        $CvsHepler->exportFileName($translate->getTranslateBySymbol('exceptionFileUploadLog').date('Y-m-d H:i:s'));
        $CvsHepler->exportHead($head);
        $CvsHepler->exportBody($data);
    }

    public static function retrunType(){
        return [
            0 => Yii::$app->sysLanguage->getTranslateBySymbol('suffix'), //'后缀',
            1 => Yii::$app->sysLanguage->getTranslateBySymbol('viruses'), //'病毒'
        ];
    }

    public static function returnRating(){
        return [
            'interception' => Yii::$app->sysLanguage->getTranslateBySymbol('intercept'), //'拦截',
            'no' => Yii::$app->sysLanguage->getTranslateBySymbol('nothing'), //' 无',
            'high'=> Yii::$app->sysLanguage->getTranslateBySymbol('high'), //'高',
            'medium' => Yii::$app->sysLanguage->getTranslateBySymbol('medium'), //'中',
            'low'=> Yii::$app->sysLanguage->getTranslateBySymbol('low')//'低'
        ];
    }
}
