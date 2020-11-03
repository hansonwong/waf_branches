<?php

namespace app\models;

use Yii;
use \yii\helpers\Url;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;
use app\logic\model\tools\SelectList;

/**
 * This is the model class for table "t_baseaccessctrl".
 *
 * @property integer $id
 * @property integer $status
 * @property string $desc
 * @property string $src_ips
 * @property string $dest_ips
 * @property string $url
 * @property string $action
 * @property integer $realid
 * @property string $type
 */
class BaseAccessCtrl extends BaseModel
{
    public $sendPipe = true;

    public static function tableName()
    {
        return 't_baseaccessctrl';
    }

    public function rulesSource()
    {
        return [
            [['status', 'realid'], 'integer'],
            [['type'], 'filter', 'filter' => function ($value) {
                return $this->url == '' ? 'B&W' : "ACCESSCTRL";
            }],
            [['realid'], 'filter', 'filter' => function($value){
                return BaseAccessCtrl::find()->max('realid')+1;
            }, 'on' => 'create'],
            [['realid'], 'required'],
            [['desc'], 'string', 'max' => 255],
            [['src_ips', 'dest_ips', 'type'], 'string', 'max' => 100],
            [['src_ips', 'dest_ips',], \app\logic\validator\IpValidator::className(), 'type' => 'mix', 'typeMix' => ['ip', 'ipWithMask'],],
            [['url'], 'string', 'max' => 1024],
            [['url'], 'url'],
            [['action'], 'string', 'max' => 45],
            [['realid'], 'unique'],
            ['status', 'in', 'range' => [0, 1]],  // 是否启用0disable 1enable
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'status' => '启用状态',
            'action' => '拦截方式',
            'src_ips' => '来源IP',
            'dest_ips' => '目标IP',
            'url' => 'url',
            'realid' => '规则ID',
            'type' => '攻击类型',
            'desc' => '说明',
        ];
    }

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        return ['query' => $query];
    }

    public function afterSave($insert, $changedAttributes)
    {
        parent::afterSave($insert, $changedAttributes);
        if($this->sendPipe) Yii::$app->wafHelper->pipe('CMD_NGINX');
    }

    public function ListSearch()
    {
        return [
            'key' => $this->modelName,
            'model' => $this,
        ];
    }

    public function ListTable()
    {
        $enable = Yii::$app->sysLanguage->getTranslateBySymbol('enable');
        $stopUse = Yii::$app->sysLanguage->getTranslateBySymbol('stopUse');

        return [
            'publicButton' => [
                ['button' => "<input type=button class='btn c_b btn_open' value='{$enable}' onclick='statusChange(0, 1);'>", 'authorityPass' => true],
                ['button' => "<input type=button class='btn c_o btn_stop' value='{$stopUse}' onclick='statusChange(0, 0);'>", 'authorityPass' => true],
            ],
            'field' => [
                'realid', 'src_ips', 'dest_ips',
                'action' => ['float' => 'c', 'type' => 'switch', 'val' => SelectList::wafActionCatArr('switch')],
                'desc', 'url',
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

        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'id' => ['showType' => 'hidden'],
                'realid' => ['showType' => 'hidden'],
                'type' => ['showType' => 'hidden'],
                'desc' => ['type' => 'textarea', 'length' => 0, 'height' => '100px'],
                'action' => SelectList::wafActionCatArr('select'),
                'status' => SelectList::enable('select'),
                'url' => [
                    'tips' => Yii::$app->sysLanguage->getTranslateBySymbol('nullIsAnything')
                        .','.Yii::$app->sysLanguage->getTranslateBySymbol('as')
                        .': http://www.example.com '
                        .Yii::$app->sysLanguage->getTranslateBySymbol('or')
                        .' https://www.example.com',
                ],
                'src_ips' => [
                    'tips' => Yii::$app->sysLanguage->getTranslateBySymbol('nullIsAnything')
                        .',' .Yii::$app->sysLanguage->getTranslateBySymbol('as')
                        .' :'.Yii::$app->sysLanguage->getTranslateBySymbol('singleIp')
                        .':127.0.0.1 '
                        .Yii::$app->sysLanguage->getTranslateBySymbol('ipSegment')
                        .':127.0.0.1/16'
                        .Yii::$app->sysLanguage->getTranslateBySymbol('or')
                        .'127.0.0.1/24',
                ],
                'dest_ips' => [
                    'tips' => Yii::$app->sysLanguage->getTranslateBySymbol('nullIsAnything')
                        .',' .Yii::$app->sysLanguage->getTranslateBySymbol('as')
                        .' :'.Yii::$app->sysLanguage->getTranslateBySymbol('singleIp')
                        .':127.0.0.1 '
                        .Yii::$app->sysLanguage->getTranslateBySymbol('ipSegment')
                        .':127.0.0.1/16'
                        .Yii::$app->sysLanguage->getTranslateBySymbol('or')
                        .'127.0.0.1/24',
                ],
            ],
            'customStr' => false,
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
                $obj->status = $status;
                $obj->save(false);
            }
        }
        Yii::$app->wafHelper->pipe('CMD_NGINX');
        Yii::$app->sysJsonMsg->msg(true, '', false);
    }
}
