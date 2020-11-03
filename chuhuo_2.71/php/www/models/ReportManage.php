<?php

namespace app\models;

use Yii;
use \yii\helpers\Url;
use app\widget\AdminListConfig;

/**
 * This is the model class for table "t_reportsmanage".
 *
 * @property integer $id
 * @property string $name
 * @property integer $type
 * @property string $desc
 * @property integer $time
 * @property string $path
 * @property integer $timetype
 * @property string $format
 */
class ReportManage extends \app\logic\model\BaseModel
{
    public static function tableName()
    {
        return 't_reportsmanage';
    }

    public function rulesSource()
    {
        return [
            [['type', 'time', 'timetype'], 'integer'],
            [['path', 'timetype', 'format'], 'required'],
            [['name'], 'string', 'max' => 100],
            [['desc', 'path'], 'string', 'max' => 255],
            [['format'], 'string', 'max' => 10],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'name' => '报表名称',
            'type' => '报表类型',
            'desc' => '报表说明',
            'time' => '生成时间',
            'path' => '路径',
            'timetype' => '报表分类',
            'format' => '格式',
        ];
    }

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => ['type', 'timetype',],
            '~' => ['name',],
            '-time' => ['time',],
        ]);
        return ['query' => $query];
    }

    public function returnType($type)
    {
        $arr = [
            '1' => Yii::$app->sysLanguage->getTranslateBySymbol('reportAttack'),
            '2' => Yii::$app->sysLanguage->getTranslateBySymbol('reportVisitFlow')
        ];
        return AdminListConfig::returnSelect($type, $arr);
    }

    public function returnTimeType($type)
    {
        $arr = [
            '1' => Yii::$app->sysLanguage->getTranslateBySymbol('reportImmediately'),
            '2' => Yii::$app->sysLanguage->getTranslateBySymbol('reportTimer')
        ];
        return AdminListConfig::returnSelect($type, $arr);
    }

    /**
     * 搜索配置
     * @return array
     */
    public function ListSearch()
    {

        return [
            'field' => [
                'name',
                'type' => $this->returnType('select'),
                'timetype' => $this->returnTimeType('select'),
                'time' => ['type' => 'betweenDateTime', 'format' => 'yyyy-MM-dd HH:mm:ss'],
            ],
            'key' => $this->modelName,
            'model' => $this,
        ];
    }

    public function ListTable()
    {
        $url = Url::to(['report-manage/report-download']);
        $tips = Yii::$app->sysLanguage->getTranslateBySymbol('systemFriendlyTips');
        $js = <<<DOC
        <script>
        function downloadFile(id){
            $.ajax({
                url: '$url',
                type: 'GET',
                data: {
                    id: id,
                },
                dataType: 'json',
                timeout: 1000,//1000毫秒后超时
                cache: false,//不缓存数据
                async: false,//同步：false,异步：true,默认true
                success: function(data){
                    console.log(data);
                    if(data.success){
                        window.open(data.data.file);
                    } else {
                        $.Layer.confirm({
                            title: '$tips', msg:'<span class=red>' + data.msg + '</span>'
                        });
                    }
                },//请求成功后执行
            });
        }
        
</script>
DOC;
        return [
            'field' => [
                'name', 'desc',
                'timetype' => ['float' => 'c', 'type' => 'switch', 'val' => $this->returnTimeType('switch')],
                'type' => ['float' => 'c', 'type' => 'switch', 'val' => $this->returnType('switch')],
                'format',
                'time' => ['type' => 'custom', 'valType' => 'datetime'],
            ],
            'recordOperation' => [
                'report-download' => ['title' => Yii::$app->sysLanguage->getTranslateBySymbol('download'), 'class' => 'bt_download list-btn', 'url' => "javascript:downloadFile(%s);"],
            ],
            'model' => $this,
            'customStr' => $js,
        ];
    }

    public function getReportFile($id, $_is_realPath=false){
        if($data = self::findOne($id)){
            $path = Yii::$app->sysPath->wafReportPath;

            if( $_is_realPath==false )
            {
                $downLoadPath = (1 == $data->timetype) ? $path['immediatelyPathDown'] : $path['timerPathDown'];
            }
            else
            {
                $downLoadPath = (1 == $data->timetype) ? $path['immediatelyPath'] : $path['timerPath'];
            }

            $downLoadPath .= $data->path;
            return $downLoadPath;
        }
        return false;
    }
}
