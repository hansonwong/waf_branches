<?php
namespace app\controllers;

class FetchTaskItemController extends \app\logic\BaseController{
	public function actionCreate()
	{
		return parent::CreateLoadParam();
	}
}
