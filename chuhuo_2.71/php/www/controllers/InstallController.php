<?php
namespace app\controllers;
use Yii;
use yii\web\Controller;
class InstallController extends Controller
{
	public function actionIndex()
	{
		//测试代码
		/*$sql_path = './../config/init_script/';
		$sql = file_get_contents($sql_path . 'init_sql.sql');
		$connection = Yii::$app->db;
		$result = $connection->createCommand($sql)->query();*/
	}
	public function actionTest(){

	}
}