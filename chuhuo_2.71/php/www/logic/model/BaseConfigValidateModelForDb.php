<?php
namespace app\logic\model;

use Yii;
use yii\base\Model;
use app\models\Config;

class BaseConfigValidateModelForDb extends Model
{
	public $modelName;//model
    protected $configSymbol = null;//配置文件

    public function __set($name, $value) {
        $this->$name = $value;
    }

    public function __construct()
	{
		parent::__construct([]);
		$className = explode("\\", get_class($this));
		$this->modelName = end($className);

        $this->initProperty();//初始化model属性

		if(null == $this->configSymbol) $this->configSymbol = $this->modelName;
		$this->loadConfig();//加载配置数据
	}

    /**
     * 初始化model属性
     */
	protected function initProperty(){
	    $scenarios = $this->getScenario();
        $attrs = $this->scenarios();

        foreach ($attrs as $scenario)
            foreach ($scenario as $item)
                if(!isset($this->$item)) $this->$item = '';
    }

    /**
     * 加载配置数据
     */
    protected function loadConfig(){
        $this->setAttributes($this->get(true));
    }

    /**
     * 初始化配置文件
     */
    protected function initModel(){
        $data = [];
        $attrs = $this->scenarios();
        foreach ($attrs as $scenario)
            foreach ($scenario as $item)
                $data[$item] = '';

        $model = new Config();
        $model->setAttributes(['symbol' => $this->configSymbol, 'json' => json_encode($data)]);
        $model->save();
        return $model;
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
        #BaseModelErrorTranslate::rulesMsgTranslate($rules);//翻译规则错误提示信息
        return $rules;
    }

    public function attributeLabels()
    {
        $attrs = $this->attributeLabelsSource();
        $attrs = Yii::$app->sysLanguage->getTranslateBySymbolAttrs($attrs);
        return $attrs;
    }

    public function attributeLabelsSource()
    {
        return [];
    }

    /**
     * 获取配置
     * @param $array true返回数组, false返回对象
     * @return mixed
     */
    public function get($array = true){
        $model = Config::findOne(['symbol' => $this->configSymbol]);
        if(!$model) $model = $this->initModel();
        return json_decode($model->json, $array);
    }

    /**
     * 保存配置
     * @return bool
     */
    public function save(){
        if (false === $this->validate()){
            Yii::$app->sysJsonMsg->errorFieldMsg(false, $this->errors);
            return false;
        } else {
            if(!$this->beforeSave()) return false;
            $data = [];
            $attrs = $this->scenarios();
            foreach ($attrs as $scenario)
                foreach ($scenario as $item)
                    $data[$item] = $this->$item;

            $model = Config::findOne(['symbol' => $this->configSymbol]);
            $model->json = json_encode($data);
            $model->save();
            $this->afterSave();
        }
        return true;
    }

    /**
     * 保存前执行
     * @return bool
     */
    public function beforeSave(){
        return true;
    }

    /**
     * 保存后执行
     * @return bool
     */
    public function afterSave(){
        return true;
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
