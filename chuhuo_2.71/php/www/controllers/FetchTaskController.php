<?php
namespace app\controllers;

use app\logic\model\AutoModelLogic;
class FetchTaskController extends \app\logic\BaseController{

	public function actionConfigTable(){
		AutoModelLogic::configTable();
	}

	//安装库/表
	public function actionInstallBase($id){
		$base = $this->findModel($id, $this->model);
		$table = FetchTaskItem::findAll(['task_id' => $id]);
		AutoModelLogic::installBase($base, $table);
	}
}
