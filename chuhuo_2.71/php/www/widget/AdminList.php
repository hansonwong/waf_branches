<?php
namespace app\widget;

use Yii;
use yii\base\Widget;
class AdminList extends Widget
{
	public $type;
	public $config;

	public function init(){
		parent::init();
	}

	public function run()
	{
		return $this->render($this->returnFile($this->type), $this->config);
	}

	public function returnFile($type){
		$file = Yii::$app->sysParams->getParamsChild(['viewPublicFile', 'public-list', $type]);
		return $file;
	}
}
?>