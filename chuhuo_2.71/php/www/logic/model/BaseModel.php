<?php
namespace app\logic\model;

use Yii;
use app\widget\AdminListConfig;

class BaseModel extends \yii\db\ActiveRecord
{
	public $modelName;

	public function __construct()
	{
		parent::__construct([]);
		$className = explode("\\", get_class($this));
		$this->modelName = end($className);
	}

    /**
     * 自定义规则
     * @return array
     */
	public function rulesSource(){
	    return [];
    }

    /**
     * 重写父规则方法,转化自定义规则为合法规则数组
     * @return array
     */
	public function rules()
    {
        $rules = $this->rulesSource();
        #自动添加自定义注释
        #BaseModelErrorTranslate::rulesMsgTranslate($rules);//翻译规则错误提示信息
        $rules[] = ['' , 'safe', 'on' => ['create', 'update']];
        return $rules;
    }


    public function attributeLabels()
    {
        $attrs = $this->attributeLabelsSource();
        return Yii::$app->sysLanguage->getTranslateByAttrs($attrs);
    }

    public function attributeLabelsSource()
    {
        return [];
    }

	public function beforeSave($insert)
	{
		if (parent::beforeSave($insert)) {
			if (false === $this->validate()) Yii::$app->sysJsonMsg->errorFieldMsg(false, $this->errors);
			if ($insert) {

			} else {

			}

			return true;
		} else {
			return false;
		}
	}

	public function parentBeforeSave($insert){
		return parent::beforeSave($insert);
	}

	public function afterSave($insert, $changedAttributes)
	{
	}

	public function afterDelete()
	{
		parent::afterDelete();
	}

    public function search($params)
    {
        $query = $this->find();
        $this->load($params);

        return ['query' => $query, 'order' => false];
    }

    public function searchFilterHelper(&$query, \yii\base\Model $obj, $filter){
        foreach ($filter as $k => $v){
            switch($k){
                case '=':#eq
                    $arr = [];
                    foreach ($v as $vv) {
                        if(is_array($vv)){
                            foreach ($vv as $vvk => $vvv) $arr[$vvk] = $vvv;
                        } else $arr[$vv] = $obj->$vv;
                    }
                    $query->andFilterWhere($arr);
                    break;
                case '!=':#not eq
                    foreach ($v as $vv) {
                        if(is_array($vv)){
                            foreach ($vv as $vvk => $vvv) $query->andFilterWhere(['!=', $vvk, $vvv]);
                        } else $query->andFilterWhere(['!=', $vv, $obj->$vv]);
                    }
                    break;
                case '~':#like
                    foreach ($v as $vv) {
                        if(is_array($vv)){
                            foreach ($vv as $vvk => $vvv)
                                $query->andFilterWhere(['like', $vvk, $vvv]);
                        } else $query->andFilterWhere(['like', $vv, $obj->$vv]);
                    }
                    break;
                case '-':#between
                    foreach($v as $vv){
                        if(is_array($vv)){
                            foreach ($vv as $vvk => $vvv){
                                if('' != $vvv[0])
                                    $query->andFilterWhere(['>=', $vvk, $vvv[0]]);
                                if('' != $vvv[1])
                                    $query->andFilterWhere(['<=', $vvk, $vvv[1]]);
                            }
                        } else {
                            if('' != ($this->$vv)[0])
                                $query->andFilterWhere(['>=', $vv, ($this->$vv)[0]]);
                            if('' != ($this->$vv)[1])
                                $query->andFilterWhere(['<=', $vv, ($this->$vv)[1]]);
                        }
                    }
                    break;
                case '-time':#between time
                    foreach($v as $vv){
                        if(is_array($vv)){
                            foreach ($vv as $vvk => $vvv){
                                if('' != $vvv[0])
                                    $query->andFilterWhere(['>=', $vvk, strtotime($vvv[0])]);
                                if('' != $vvv[1])
                                    $query->andFilterWhere(['<=', $vvk, strtotime($vvv[1])]);
                            }
                        } else {
                            if('' != ($this->$vv)[0])
                                $query->andFilterWhere(['>=', $vv, strtotime(($this->$vv)[0])]);
                            if('' != ($this->$vv)[1])
                                $query->andFilterWhere(['<=', $vv, strtotime(($this->$vv)[1])]);
                        }
                    }
                    break;
            }
        }
    }

	/**
	 * 搜索配置
	 * @return array
	 */
	public function ListSearch()
	{
        return [
            'key' => $this->modelName,
            'model' => $this,
        ];
	}

	/**
	 * 列表配置
	 * @param $dataProvider
	 * @return array
	 */
	public function ListTable($dataProvider)
	{
        return [
            'publicButton' => [],
            'data' => $dataProvider,
            'field' => [],
            'recordOperation' => [],
            'model' => $this
        ];
	}

	/**
	 * 字段修改、添加配置
	 * @return array
	 */
	public function ListField()
	{
		return false;
	}
}
