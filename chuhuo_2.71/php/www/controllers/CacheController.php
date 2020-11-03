<?php
namespace app\controllers;

use Yii;

class CacheController extends \app\logic\BaseController
{
	public function actionIndex()
	{
		return $this->renderPartial('index', []);
	}

	public function actionCleanCache()
	{
		$cache = Yii::$app->cache;
		$data = Yii::$app->request->post('data');
		switch ($data) {
			case 'all' :
				$result = $cache->flush();
				break;
			case 'proMenu' :
				$result = $cache->delete($data);
				break;

			default :
				;
		}
        Yii::$app->sysJsonMsg->msg((1 == $result) ? true : false, '清除成功');
	}
}
