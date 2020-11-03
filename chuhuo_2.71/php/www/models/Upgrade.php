<?php
namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use yii\base\Model;
use yii\web\UploadedFile;

class Upgrade extends Model
{
	public $rules_file;
	
	public function rulesSource()
	{
		return [
			[['rules_file'],'file','skipOnEmpty'=>false],
		];
	}
	
	public function upload()
	{
		if($this->validate()){
			$this->rules_file->saveAs('web\cache'.$this->rules_file.baseName.'.'.$this->rules_file->extension);
		} else {
			return false;
		}
	}
}

?>