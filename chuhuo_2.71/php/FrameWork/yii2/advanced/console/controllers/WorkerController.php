<?php
namespace console\controllers;//\script;
use Yii;
use yii\console\Controller;
use shmilyzxt\queue\Worker;
class WorkerController extends Controller
{
	/*public function actionIndex(){
		echo '111';
	}*/

	public function actionListen($queueName='default',$attempt=10,$memeory=128,$sleep=3 ,$delay=0){
		Worker::listen(\Yii::$app->queue,$queueName,$attempt,$memeory,$sleep,$delay);
	}
}