<?php
namespace app\logic\validator;
use Yii;

class ArrayValidator extends BaseValidator
{
	public $type;

	/**
	 * @inheritdoc
	 */
	public function validateAttribute($model, $attribute)
	{
		$value = $model->$attribute;
		if(!is_array($value)){
			$this->addError($model, $attribute, '必须是数组');
		}
	}
}