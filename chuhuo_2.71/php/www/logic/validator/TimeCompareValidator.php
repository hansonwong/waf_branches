<?php
namespace app\logic\validator;
use Yii;

class TimeCompareValidator extends BaseValidator
{
	public $TimeType;
	public $CompareField;

	/**
	 * @inheritdoc
	 */
	public function validateAttribute($model, $attribute)
	{
		$value = $model->$attribute;
		$comparename = $this->CompareField;
		$compare = $model->$comparename;

		$lable = $model->attributeLabels();
		switch($this->TimeType){
			case 'str' :
				$value = strtotime($value);
				$compare = strtotime($compare);
				break;
			default : ;
		}
		if('' != $compare) {
			if($value > $compare) $this->addError($model, $attribute, $lable[$attribute].'必须小于'.$lable[$comparename]);
		}
	}
}