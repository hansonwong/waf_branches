<?php
namespace app\controllers;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\ReturnFetcherAutoModel;
class FetchAutoModelController extends \app\logic\BaseController{
	public $model = '\\app\\logic\\model\\FetcherAutoModel';

	public function actionSearchResult(){
		$CM = $this->getSearchModelAndCondition();
		return $this->getSearchQueryResult($CM);
	}

	public function getSearchModelAndCondition(){
		$get = Yii::$app->request->get();
		$tbIdKey = Yii::$app->sysParams->getParamsChild(['tableAutoId', 'fetcher']);
		$primaryModel = ReturnFetcherAutoModel::getModel();
		$primaryModel = new $primaryModel($get["{$tbIdKey}"]);
		$secondModel = ReturnFetcherAutoModel::getModel();
		$secondModel = new $secondModel($get["f{$tbIdKey}"]);
		$id = $get[$tbIdKey];

		$globalVar = [];
		eval($primaryModel::$config->field_global_var);
		$primary_field_global_var = $globalVar;
		eval($secondModel::$config->field_global_var);
		$second_field_global_var = $globalVar;
		if(isset($second_field_global_var['searchBy']['other'][$id]))
			$condition = $second_field_global_var['searchBy']['other'][$id];
		elseif(isset($primary_field_global_var['searchBy']['self']))
			$condition = $primary_field_global_var['searchBy']['self'];
		else $condition = [];
		return ['c' => $condition, 'm' => $primaryModel];
	}

	public function getSearchQueryResult($cm){
		$post = Yii::$app->request->post();
		$query = $cm['m']->find();
		$c = $cm['c'];
		foreach($c as $ck => $cv){
			switch($ck){
				case 'fix':if(is_array($cv))$query->where($cv);break;
				case 'selfField':
				case 'customField':
					if(isset($cv['eq']) && is_array($cv['eq'])){
						foreach ($cv['eq'] as $k => $v) $query->andFilterWhere([$k => $post[$v]]);
					}
					if(isset($cv['like']) && is_array($cv['like'])){
						foreach ($cv['like'] as $k => $v) $query->andFilterWhere(['like', $k, $post[$v]]);
					}
					if(isset($cv['between']) && is_array($cv['between'])){
						foreach ($cv['between'] as $k => $v) $query->andFilterWhere(AdminListConfig::FilterNum($k, $post[$v]));
					}
					break;
			}
		}
		return json_encode($query->asArray()->all());
	}
}
