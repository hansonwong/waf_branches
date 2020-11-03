<?php
namespace app\logic\model;

use Yii;
use app\widget\AdminListConfig;
use app\models\FetchTaskItem;
use app\logic\sys\SysParams;
use app\logic\model\BaseModel;
class FetcherAutoModel extends BaseModel
{
	public static $db, $config, $tbId, $globalVar;

	public function __construct($target = null)
	{
		parent::__construct();
		if($target){
			if(0 == $target) return null;
			self::$tbId = $target;
		} else {
			$tbIdKey = SysParams::getParamsChild(['tableAutoId', 'fetcher']);
			$get = Yii::$app->request->get();
			self::$tbId = $get[$tbIdKey];
		}
		self::$config = $config = FetchTaskItem::findOne(self::$tbId);

		$dbInfo = $config->dbInfo;

		if(!$dbInfo) Yii::$app->end();
		self::$db = "db{$dbInfo->id}";

		if (!Yii::$app->has(self::$db)) {
			$db = Yii::$app->components['db'];
			$db['dsn'] = "mysql:host={$dbInfo->host};dbname={$dbInfo->db}";
			$db['username'] = $dbInfo->user;
			$db['password'] = $dbInfo->pwd;
			Yii::$app->set(self::$db, $db);
		}

		$globalVar = [];
		eval($config->field_global_var);
		self::$globalVar = $globalVar;
	}

	public function construct($target){
		$modelName = __CLASS__;
		return new $modelName($target);
	}

	public function getMagicModel($relationName){
		$config = self::$globalVar['magicGetModel'][$relationName];
		$relation = $config['relation'];
		$modelName = __CLASS__;
		$model = new $modelName($config['modelId']);
		$result = $model->find()->where([$relation['relField'] => $this->$relation['selfField']]);
		$result = ('one' == $relation['has']) ? $result->one() : $result->all();
		return $result;
	}

	public static function getDb()
	{
		return Yii::$app->get(self::$db);
	}

	public static function tableName()
	{
		return self::$config->tb;
	}

	public function rules()
	{
		$result = null;
		eval(self::$config->field_rules);
		return $result;
	}

	public function attributeLabels()
	{
		$result = null;
		eval(self::$config->field_attribute_label);
		return $result;
	}

	public function search($params)
	{
		$query = $this->find();
		$this->load($params);

		$searchSet = [];
		eval(self::$config->field_search);
		$eq = isset($searchSet['eq']) ? $searchSet['eq'] : [];
		$like = isset($searchSet['like']) ? $searchSet['like'] : [];
		$betweenNum = isset($searchSet['betweenNum']) ? $searchSet['betweenNum'] : [];
		$betweenTime = isset($searchSet['betweenTime']) ? $searchSet['betweenTime'] : [];

		foreach ($eq as $item) $query->andFilterWhere([$item => $this->$item]);
		foreach ($like as $item) $query->andFilterWhere(['like', $item, $this->$item]);
		foreach ($betweenNum as $item) $query->andFilterWhere(AdminListConfig::FilterNum($item, $this->$item));
		foreach ($betweenTime as $item){
			if ('' != $this->$item) {
				$betweenTimeItem = explode('~', $this->$item);
				if(2 == count($betweenTimeItem)){
					$query->andFilterWhere(['>', $item, strtotime($betweenTimeItem[0])]);
					$query->andFilterWhere(['<', $item, strtotime($betweenTimeItem[1])]);
				}
			}
		}
        return ['query' => $query, 'order' => false];
	}

	/**
	 * 搜索配置
	 * @return array
	 */
	public function ListSearch()
	{
		$searchSet = [];
		$customHtml = [];
		eval(self::$config->field_search_box);

        return [
            'field' => $searchSet,
            'key' => $this->modelName,
            'model' => $this,
            'customStr' => self::ListSearchCustomHtml($customHtml),
        ];
	}

	public static function ListSearchCustomHtml($custom){
		$customStr = '';
		foreach ($custom as $type => $fields){
			switch($type){
				case 'search-time-between' :
					foreach ($fields as $item)
						$customStr .= AdminListConfig::returnEmptyController(SysParams::getParamsChild(['viewPublicFile', 'search-html', 'search-time-between-by-bootstrap-modal']), ['config' => $item]);
					//['field' => 'create_time', 'label' => '创建时间']
					break;
				case 'search-time' :
					if(0 < count($fields))
						$customStr .= AdminListConfig::returnEmptyController(SysParams::getParamsChild(['viewPublicFile', 'search-html', 'search-time-by-jquery_ui_datepicker']), ['timeKey' => $fields]);
					break;
				case 'search-keyword-for-id' :
					foreach ($fields as $item){
						if(!isset($item['url']) && isset($item['urlArgs'])){
							$tbIdKey = SysParams::getParamsChild(['tableAutoId', 'fetcher']);
							$item['urlArgs']["f{$tbIdKey}"] = self::$tbId;
							$item['url'] = "fetch-auto-model/search-result?".http_build_query($item['urlArgs']);
						}
						$customStr .= AdminListConfig::returnEmptyController(SysParams::getParamsChild(['viewPublicFile', 'search-html', 'search-keyword-for-id-by-bootstrap-modal']), ['config' => $item]);
					}
					//['field' => 'school_id', 'url' => 'activity-beauty-school/search-school', 'label' => '学校', 'data' => 'id:name', 'conditionFields' => ['name']]
					//['field' => 'age', 'urlArgs' => ['tbFetcherId' => 3], 'label' => '学校', 'data' => 'id:name', 'conditionFields' => ['name']]
					break;
				case 'radio-for-id' :
					foreach ($fields as $item){
						if(!isset($item['url']) && isset($item['urlArgs'])){
							$tbIdKey = SysParams::getParamsChild(['tableAutoId', 'fetcher']);
							$item['urlArgs']["f{$tbIdKey}"] = self::$tbId;
							$item['url'] = "fetch-auto-model/search-result?".http_build_query($item['urlArgs']);
						}
						$customStr .= AdminListConfig::returnEmptyController(SysParams::getParamsChild(['viewPublicFile', 'search-html', 'radio-for-id-by-bootstrap-modal']), ['config' => $item]);
					}
					//['field' => 'age', 'urlArgs' => ['tbFetcherId' => 3], 'label' => '优惠券/红包', 'data' => 'id:name,name', 'conditionFields' => ['name']]
					//['field' => 'refer_id', 'url' => 'lottery-turntable-item/type-search', 'label' => '优惠券/红包', 'data' => 'id:coupon_name,name', 'conditionFields' => ['type']]
					break;
				case 'checkbox-for-id' :
					foreach ($fields as $item){
						if(!isset($item['url']) && isset($item['urlArgs'])){
							$tbIdKey = SysParams::getParamsChild(['tableAutoId', 'fetcher']);
							$item['urlArgs']["f{$tbIdKey}"] = self::$tbId;
							$item['url'] = "fetch-auto-model/search-result?".http_build_query($item['urlArgs']);
						}
						$customStr .= AdminListConfig::returnEmptyController(SysParams::getParamsChild(['viewPublicFile', 'search-html', 'checkbox-for-id-by-bootstrap-modal']), ['config' => $item]);
					}
					//['field' => 'age', 'urlArgs' => ['tbFetcherId' => 3], 'label' => '优惠券', 'data' => 'id:name,name', 'split' => ',', 'conditionFields' => ['name']]
					//['field' => 'coupons', 'url' => 'coupon/search-coupon', 'label' => '优惠券', 'data' => 'id:coupon_name', 'split' => ',', 'conditionFields' => ['type']]
					break;
				default:;
			}
		}
		return $customStr;
	}

	/**
	 * 列表配置
	 * @param $dataProvider
	 * @return array
	 */
	public function ListTable($dataProvider)
	{
		$public_button_default = ['create' => ['onclick' => AdminListConfig::returnCreateUrl(), 'title' => '添加']];
		$public_button = [];
		$clos = [];
		eval(self::$config->field_table);
		$frameSize = SysParams::getParams('hui-frame-size');
		$tbIdKey = SysParams::getParamsChild(['tableAutoId', 'fetcher']);
		$tbIdValue = self::$tbId;

        return [
            'publicButton' => array_merge($public_button, $public_button_default),
            'data' => $dataProvider,
            'field' => $clos,
            'recordOperation' => [
                'fetcher' => ['title' => '爬虫运动', 'url' => 'fetcher?id=%s', 'type' => 'box'],
                'view' => ['title' => '查看', 'url' => "javascript:data_view(\"查看\", \"%s&{$tbIdKey}={$tbIdValue}\", \"{$frameSize['width']}\", \"{$frameSize['height']}\");"],
                'update' => ['title' => '修改', 'url' => "javascript:data_edit(\"修改\", \"%s&{$tbIdKey}={$tbIdValue}\", \"{$frameSize['width']}\", \"{$frameSize['height']}\");"],
                'delete' => ['title' => '删除', 'url' => "javascript:data_delete(this, \"%s\", \"{$tbIdKey}={$tbIdValue}\");"],
            ],
            'model' => $this
        ];
	}

	/**
	 * 字段修改、添加配置
	 * @return array
	 */
	public function ListField()
	{
		$edit_create = [];
		$edit_modify = [];
		$customHtml = [];
		eval(self::$config->field_edit);

		$type = AdminListConfig::ListFieldScenarios('common', $this);
		switch ($type) {
			case 'create' :
				$field = $edit_create;
				break;
			case 'update' :
				$field = $edit_modify;
				break;
			default :;
		}
		$field['fieldKey'] = $this->modelName;
		$field['field'] = $this->attributeLabels();
		$field['customStr'] = self::ListSearchCustomHtml($customHtml);
		return $field;
	}

	public function returnSelectByArr($type, $arr){
		return AdminListConfig::returnSelect($type, $arr);
	}

	public function returnSelectByModel($config){
		$modelName = __CLASS__;
		$model = new $modelName($config['modelId']);
		$arr = $model->find()->where($config['condition'])->all();
		return AdminListConfig::returnSelect($config['type'], $arr, $config['key-val']);
	}

	public static function getFilePath(){
		return __FILE__;
	}
}
