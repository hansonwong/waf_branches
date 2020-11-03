<?php
namespace app\logic\validator;
use Yii;

class NumberValidator extends BaseValidator
{
	public $type;
	public $decimalMax;
	public $decimalMin;
	public $decimal;

	/**
	 * @inheritdoc
	 */
	public function validateAttribute($model, $attribute)
	{
		$value = $model->$attribute;

		if(!is_numeric($value)) $this->addError($model, $attribute, '必须是数字');
		switch($this->type){
			case 'integer' :
			case 'integerMinus' :
			case 'integerPositive' :
				if(!is_int($value)) $this->addError($model, $attribute, '必须是整数');
				break;

			case 'float' :
			case 'floatMinus' :
			case 'floatPositive' :
				if(!is_float($value + 0)) $this->addError($model, $attribute, '必须是小数');
				$DecimalCount = self::getDecimalCount($value);
				if($this->decimal){
					if($this->decimal != $DecimalCount) $this->addError($model, $attribute, "小数点位数必须是{$this->decimal}位");
				}
				if($this->decimalMax){
					if($this->decimalMax < $DecimalCount) $this->addError($model, $attribute, "小数点位数最多不能超过{$this->decimalMax}位");
				}
				if($this->decimalMin){
					if($this->decimalMin > $DecimalCount) $this->addError($model, $attribute, "小数点位数不能少于{$this->decimalMin}位");
				}
				break;

			default : ;
		}
		switch($this->type){
			case 'integer' :
				break;
			case 'integerMinus' :
				if(0 < $value) $this->addError($model, $attribute, '必须是负整数');
				break;
			case 'integerPositive' :
				if(0 > $value) $this->addError($model, $attribute, '必须是正整数');
				break;
			case 'float' :
				break;
			case 'floatMinus' :
				if(0 < $value) $this->addError($model, $attribute, '必须是负小数');
				break;
			case 'floatPositive' :
				if(0 > $value) $this->addError($model, $attribute, '必须是正小数');
				break;
			default : ;
		}
	}

	public static function getDecimalCount($value){
		$count = 0;
		$temp = explode ('.', $value);
		if (sizeof ( $temp ) > 1) {
			$decimal = end($temp);
			$count = strlen($decimal);
		}
		return $count;
	}
}