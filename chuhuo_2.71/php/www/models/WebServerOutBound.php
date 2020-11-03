<?php

namespace app\models;

use Yii;
use app\logic\model\BaseModel;
use app\logic\model\tools\SelectList;
use app\widget\AdminListConfig;
/**
 * This is the model class for table "t_webserver_outbound".
 *
 * @property integer $id
 * @property integer $is_use
 * @property string $sip
 * @property string $dip
 * @property string $dport
 */
class WebServerOutBound extends BaseModel
{
    public $sendPipe = true;

    public static function tableName()
    {
        return 't_webserver_outbound';
    }

    public function rulesSource()
    {
        return [
            [['is_use'], 'integer'],
            [['is_use'], 'in', 'range'=>[0, 1]],
            [['sip', 'dip'], 'string', 'max' => 15],
            [['dport'], 'string', 'max' => 5],
            [['dport'], 'integer','min' => 1, 'max' => 65535],
            [['sip', 'dip', 'dport'], 'unique', 'targetAttribute' => ['sip', 'dip', 'dport']],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'id' => 'ID',
            'is_use' => '执行动作',
            'sip' => '源IP',
            'dip' => '目标IP',
            'dport' => '目标端口',
        ];
    }

    public function afterSave($insert, $changedAttributes)
    {
        parent::afterSave($insert, $changedAttributes);
        if($this->sendPipe) Yii::$app->wafHelper->pipe('CMD_WEBOUTRULE');
    }

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => ['sip', 'dip', 'dport', 'is_use'],
        ]);
        return ['query' => $query];
    }

    public function ListSearch()
    {
        return [
            'field' => [
                'sip',
                'dip',
                'dport',
                'is_use' => SelectList::blackWhiteEnable('select'),
            ],
            'key' => $this->modelName,
            'model' => $this,
        ];
    }

    public function ListTable()
    {
        $toBlackList = Yii::$app->sysLanguage->getTranslateBySymbol('toBlackList');
        $toWhiteList = Yii::$app->sysLanguage->getTranslateBySymbol('toWhiteList');

        return [
            'publicButton' => [
                ['button' => "<input type=button class='btn c_b btn_hmd' value='{$toBlackList}' onclick='statusChange(0, 1);'>", 'authorityPass' => true],
                ['button' => "<input type=button class='btn c_o btn_bmd' value='{$toWhiteList}' onclick='statusChange(0, 0);'>", 'authorityPass' => true],
            ],
            'field' => [
                'sip',
                'dip',
                'dport',
                'is_use' => ['float' => 'c', 'type' => 'switch', 'val' => SelectList::blackWhiteEnable('switch')],
            ],
            'model' => $this,
            'customStr' => \Yii::$app->view->renderFile('@app/views/rule-custom-defend-policy/list-component.php'),
        ];
    }

    public function ListField()
    {
        $type = AdminListConfig::ListFieldScenarios('common', $this);
        $fieldKey = $this->modelName;

        $fieldType = [
            'id' => ['showType' => 'hidden'],
            'is_use' => SelectList::blackWhiteEnable('select'),
        ];
        switch ($type) {
            case 'create' :
                break;
            case 'update' :
                break;
            default :
                ;
        }
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => $fieldType,
            'customStr' => false,
        ];
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
                $obj->is_use = $status;
                $obj->save(false);
            }
        }
        Yii::$app->wafHelper->pipe('CMD_WEBOUTRULE');
        Yii::$app->sysJsonMsg->msg(true, '', false);
    }
}
