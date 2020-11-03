<?php
namespace app\logic\validator;
use Yii;

class IpValidator extends BaseValidator
{
    //验证类型
	public $type;
    //$typeMix = ['ip', 'ipInterval'];//混合验证
	public $typeMix = null;

	public static function relationList(){
	    $t = Yii::$app->sysLanguage;
	    return [
	        'ip' => ['fun' => 'validateIp', 'msg' => $t->getTranslateBySymbol('ipAddressIsNotLegal')],
            'ipInterval' => ['fun' => 'validateIpInterval', 'msg' => $t->getTranslateBySymbol('ipIntervalIsNotLegal')],
            'ipIntervalFor4' => ['fun' => 'validateIpIntervalFor4', 'msg' => $t->getTranslateBySymbol('ipIntervalIsNotLegal')],
            'ipWithMask' => ['fun' => 'validateIpWithMask', 'msg' => $t->getTranslateBySymbol('ipWithMaskIsNotLegal')],
        ];
    }

	/**
	 * @inheritdoc
	 */
	public function validateAttribute($model, $attribute)
	{
		$value = $model->$attribute;
		if('' == $value) return;

		$relationList = self::relationList();
		switch($this->type){
		    case 'ip':
            case 'ipInterval':
            case 'ipWithMask':
                $fun = $relationList[$this->type]['fun'];
                if(!self::$fun($value))
                    $this->addError($model, $attribute, Yii::$app->sysLanguage->getTranslateBySymbol($relationList[$this->type]['msg']));
            case 'mix':
                if(!self::validateMix($value, $this->typeMix))
                    $this->addError($model, $attribute, Yii::$app->sysLanguage->getTranslateBySymbol('parameterError'));
                break;
        }
	}

    /**
     * 验证IP
     * @param $value
     * @return bool
     */
	public static function validateIp($value){
        preg_match('/^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/', $value, $match);
        return $match[0] ?? false;
    }

    /**
     * 验证IP区间
     * @param $value
     * @return bool
     */
    public static function validateIpInterval($value){
	    $ip = explode('-', $value);
	    if(2 != count($ip)) return false;
	    if(!(self::validateIp($ip[0]) && self::validateIp($ip[1]))) return false;
	    $ip1 = explode('.', $ip[0]);
	    $ip2 = explode('.', $ip[1]);

	    function checkNum($num1, $num2){
            return $num1 < $num2;
        }

        function checkEqual($num1, $num2){
            return $num1 == $num2;
        }

        for($i = 0; $i < 4; $i++){
            if(checkNum($ip1[$i], $ip2[$i])) return true;
            if(!checkEqual($ip1[$i], $ip2[$i])) return false;
        }
	    return true;
    }

    /**
     * 验证IP区间(最后一位)
     * @param $value
     * @return bool
     */
    public static function validateIpIntervalFor4($value){
        $ip = explode('-', $value);
        if(2 != count($ip)) return false;
        if(!(self::validateIp($ip[0]) && self::validateIp($ip[1]))) return false;
        $ip1 = explode('.', $ip[0]);
        $ip2 = explode('.', $ip[1]);

        function checkNum($num1, $num2){
            return $num1 < $num2;
        }

        function checkEqual($num1, $num2){
            return $num1 == $num2;
        }

        for($i = 0; $i < 3; $i++){
            if(!checkEqual($ip1[$i], $ip2[$i])) return false;
        }
        return (checkNum($ip1[3], $ip2[3]));
    }

    /**
     * 验证IP和MASK
     * @param $value
     * @return bool
     */
    public static function validateIpWithMask($value){
        $arr = explode('/', $value);
        if(!self::validateIp($arr[0])) return false;

        $ipNum = explode('.', $arr[0]);
        $mask = $arr[1];

        if($mask == 24){
            if( ! (($ipNum[3]=='0')&&($ipNum[2]!='0')&&($ipNum[1]!='0')) ) return false;
        }elseif($mask == 16){
            if( ! (($ipNum[3]=='0')&&($ipNum[2]=='0')&&($ipNum[1]!='0')) ) return false;
        }elseif($mask == 8){
            if( ! (($ipNum[3]=='0')&&($ipNum[2]=='0')&&($ipNum[1]=='0')) ) return false;
        } else return false;

        return true;
    }

    /**
     * 混合验证
     */
    public static function validateMix($value, $typeMix){
        $sym = false;
        if(null != $typeMix){
            $relationList = self::relationList();
            foreach($typeMix as $type){
                $fun = $relationList[$type]['fun'];
                if(self::$fun($value)){
                    $sym = true;
                    break;
                }
            }
        }
        return $sym;
    }
}