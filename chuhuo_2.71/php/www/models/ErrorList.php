<?php

namespace app\models;

use Yii;
use app\logic\model\BaseModel;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;
use app\widget\AdminListConfig;
/**
 * This is the model class for table "t_errorlist".
 *
 * @property integer $id
 * @property string $status_code
 * @property integer $prompt_type
 * @property string $prompt_file
 * @property string $prompt_content
 * @property string $desc
 * @property integer $status
 */
class ErrorList extends BaseModel
{
    public $sendPipe = true;

    public static function tableName()
    {
        return 't_errorlist';
    }

    public function rulesSource()
    {
        return [
            [['status_code', 'prompt_type', 'prompt_content'], 'required'],
            [['status_code'], 'in', 'range' => ['403', '404', '502', '503']],
            [['status_code'], 'unique'],
            [['status'], 'default', 'value' => 0],
            [['status'], 'filter', 'filter' => function ($value) {
                return 0;
            }, 'on' => 'update'],
            [['prompt_type', 'status'], 'integer'],
            [['prompt_content'], 'string'],
            [['status_code'], 'string', 'max' => 20],
            [['prompt_file'], 'string', 'max' => 100],
            [['desc'], 'string', 'max' => 255],
            [['prompt_file'], function ($attribute, $params) {
                if(1 != $this->prompt_type) return;
                if(0 != $_FILES['UploadSingleFile']['error'][$attribute] && $this->$attribute) return;
                $model = new \app\logic\model\UploadSingleFile([
                    'key' => $attribute,
                    'path' => Yii::$app->sysPath->cachePath."data/errorpages/{$this->$attribute}",
                    'rule' => ['maxSize'=>3 * 1024*1024],
                ]);
                if(!$model->instanceSave())
                    $this->addError($attribute, $model->getErrorsInfoString());
                $this->$attribute = "{$this->status_code}.html";
            }, 'skipOnEmpty' => false, 'on' => ['create', 'update']],
        ];
    }

    public function afterSave($insert, $changedAttributes)
    {
        parent::afterSave($insert, $changedAttributes);

        if(!$this->sendPipe) return;
        //自定义文件上传
        if(1 == $this->prompt_type)
            Yii::$app->wafHelper->pipe('CMD_NGINX');

        //使用模板，提示文字
        if(2 == $this->prompt_type)
            Yii::$app->wafHelper->pipe("CMD_GEN_ERRORPAGE|{$this->status_code}");
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'status_code' => '错误页面类型',
            'prompt_type' => '提示类型',
            'prompt_file' => '自定义文件',
            'prompt_content' => '页面提示文字',
            'desc' => '备注',
            'status' => '生效状态',
        ];
    }

    public function returnPromptType($type){
        $arr = [1 => Yii::$app->sysLanguage->getTranslateBySymbol('pagefile'), 2 => Yii::$app->sysLanguage->getTranslateBySymbol('pagePromptText')];
        return AdminListConfig::returnSelect($type, $arr);
    }

    public function ListSearch()
    {
        return [
            'field' => [],
            'key' => $this->modelName,
            'model' => $this,
        ];
    }

    public function ListTable()
    {
        return [
            'field' => [
                'status_code',
                'prompt_type' => ['type' => 'switch', 'val' => $this->returnPromptType('switch')],
                'prompt_file', 'prompt_content',
                'status' => ['type' => 'callback', 'val' => function($obj, $val){
                    $class = (1 == $val) ? 'bt_qyan' : 'bt_tyan';
                    $str =  (1 == $val) ? 'enable' : 'stopUse';
                    $status = 1 == $val ? 0 : 1;
                    $str = Yii::$app->sysLanguage->getTranslateBySymbol($str);
                    return "<input type=button class='qt {$class}' onclick='statusChange({$obj['id']}, {$status});' title='{$str}'>";
                }],
            ],
            'model' => $this,
            'customStr' => \Yii::$app->view->renderFile('@app/views/rule-custom-defend-policy/list-component.php'),
        ];
    }

    public function ListField()
    {
        $type = AdminListConfig::ListFieldScenarios('common', $this);
        $fieldKey = $this->modelName;

        #获取继承模板配置
        $groupModelIdConfig = SelectList::ruleModelGroup('select');
        #unset继承模板配置中当前id
        if(null !== $this->id) unset($groupModelIdConfig['data'][$this->id]);

        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'id' => ['showType' => 'hidden'],
                'status' => ['showType' => 'hidden'],
                'prompt_type' => $this->returnPromptType('radio'),
                'status_code' => AdminListConfig::returnSelect('select', [403 => 403, 404 => 404, 502 => 502, 503 => 503]),
                'prompt_file' => ['type' => 'fileWithVal'],
                'prompt_content',
                'desc',
            ],
        ];
        switch ($type) {
            case 'create' :
                break;
            case 'update' :
                break;
            default :
                ;
        }
        return $field;
    }

    public static function updateStatus(){
        $model = new self;
        $query = Yii::$app->request->bodyParams;
        $id = $query['id'];
        $status = $query['status'];
        if(!is_array($id)) return false;
        foreach ($id as $item) {
            if ('' != $item) {
                $obj = $model->findOne($item);
                $obj->sendPipe = false;
                $obj->status = $status;
                $obj->save(false);
            }
        }
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        Yii::$app->sysJsonMsg->msg(true, '', false);
    }

    public static function recordDelete()
    {
        $query = Yii::$app->request->bodyParams;
        $id = $query['id'];
        if(!is_array($id)) return false;

        $result = self::find()->where(['status' => 1, 'id' => $id])->count();
        if($result>0)
            Yii::$app->sysJsonMsg->msg(false, Yii::$app->sysLanguage->getTranslateBySymbol('stopBeforeDeleting'));

        $arr = self::findAll(['id' => $id]);
        $filePath = Yii::$app->sysPath->cachePath."data/errorpages/";
        foreach($arr as $v)
        {
            //删除自定义文件
            $fileName = "{$filePath}{$v->prompt_file}";
            if(file_exists($fileName)) @unlink($fileName);

            // 删除使用模板的文件
            $fileName = Yii::$app->sysPath->cachePath."data/mode/{$v->status_code}.html";
            if(!file_exists($fileName)) @unlink($fileName);

            $v->delete();
        }

        //写入命名管道
        Yii::$app->wafHelper->pipe('CMD_NGINX');

        Yii::$app->sysJsonMsg->msg(true, '', false);
    }
}
