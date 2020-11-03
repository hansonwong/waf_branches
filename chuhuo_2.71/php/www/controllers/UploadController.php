<?php
namespace app\controllers;

use Yii;
use yii\web\Controller;
use app\logic\sys\SysAuthority;
class UploadController extends Controller
{
	public function beforeAction($action){
		if (false == Yii::$app->request->isGet &&
			true == in_array($action->id, $this->noCsrf)) {
			$this->enableCsrfValidation = false;
		}

		if (parent::beforeAction($action)) {
			return SysAuthority::singleAuthorityByAction($action);
		} else {
			return false;
		}
	}

	protected $noCsrf = ['ueditor-img'];

	public function actionIndex()
	{
		$config = explode('|', $_REQUEST['uploadFileCurrent']);
		$FieldId = $config[0];
		$FieldType = $config[1];
		$FieldSize = $config[2];
		$FieldShow = $config[3];

		$avatar = $this->Upload($FieldId);//Uploader::upload($FieldId);
		if (is_numeric($avatar)) {
			echo '<li id="id"></li><li id="data">F</li>';
		} else {
			echo "<li id='id'>{$FieldId}</li>";
			echo "<li id='data'>{$avatar}</li>";
			echo "<li id='show'>{$FieldShow}</li>";
		}
	}

	public function actionUeditorImg()
	{
		if (Yii::$app->request->get('action') === 'config') {
			$url = '/assets/h-ui/lib/ueditor/1.4.3/php/controller.php?action=config';
			header('Location: ' . $url);
			die();
		}

		$avatar = Uploader::upload('upfile');
		if (is_numeric($avatar)) {
			$state = '';
			$url = '';
        } else {
			$state = 'SUCCESS';
			$url = $avatar;
		}

		$arr = [
			"state" => $state,          //上传状态，上传成功时必须返回"SUCCESS"
			"url" => $url,            //返回的地址
			"title" => "",          //新文件名
			"original" => "",       //原始文件名
			"type" => "",            //文件类型
			"size" => "",           //文件大小
		];

		echo json_encode($arr);
	}

	public function Upload($name){

	}
}
