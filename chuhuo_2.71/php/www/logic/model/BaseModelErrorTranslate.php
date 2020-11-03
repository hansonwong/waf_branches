<?php
namespace app\logic\model;

use Yii;

class BaseModelErrorTranslate
{
    public static function rulesMsgTranslate(&$rules){
        foreach($rules as $k => $v){
            $item = $rules[$k];
            if(isset($item['message'])) continue;
            if(isset($item['msgSymbol'])) $rules[$k]['message'] = Yii::$app->sysLanguage->getTranslateBySymbol($item['msgSymbol']);
            else {
                switch($item[1]){
                    case 'double':
                        self::double($rules[$k]);break;
                    case 'email':
                        self::email($rules[$k]);break;
                    case 'file':
                        self::file($rules[$k]);break;
                    case 'in':
                        self::in($rules[$k]);break;
                    case 'integer':
                        self::integer($rules[$k]);break;
                    case 'number':
                        self::number($rules[$k]);break;
                    case 'required':
                        self::required($rules[$k]);break;
                    case 'string':
                        self::string($rules[$k]);break;
                    case 'unique':
                        self::unique($rules[$k]);break;
                    case 'url':
                        self::url($rules[$k]);break;
                    default:;
                }
            }
        }
    }

    public static function double(&$item){
        $max = isset($item['max']) ?? false;
        $min = isset($item['min']) ?? false;
        if(false !== $max && false !== $min){
            $symbol = Yii::$app->sysLanguage->getTranslateBySymbol('validateDoubleInteval');
            $symbol = sprintf($symbol, $min, $max);
        } elseif(false !== $max){
            $symbol = Yii::$app->sysLanguage->getTranslateBySymbol('validateDoubleMax');
            $symbol = sprintf($symbol, $max);
        } elseif(false !== $min){
            $symbol = Yii::$app->sysLanguage->getTranslateBySymbol('validateDoubleMin');
            $symbol = sprintf($symbol, $min);
        } else $symbol = Yii::$app->sysLanguage->getTranslateBySymbol('validateDouble');
        $item['message'] = $symbol;
    }

    public static function email(&$item){
        $item['message'] = Yii::$app->sysLanguage->getTranslateBySymbol('validateEmail');
    }

    public static function file(&$item){

    }

    public static function in(&$item){

    }

    public static function number(&$item){
        $max = isset($item['max']) ?? false;
        $min = isset($item['min']) ?? false;
        if(false !== $max && false !== $min){
            $symbol = Yii::$app->sysLanguage->getTranslateBySymbol('validateNumberInteval');
            $symbol = sprintf($symbol, $min, $max);
        } elseif(false !== $max){
            $symbol = Yii::$app->sysLanguage->getTranslateBySymbol('validateNumberMax');
            $symbol = sprintf($symbol, $max);
        } elseif(false !== $min){
            $symbol = Yii::$app->sysLanguage->getTranslateBySymbol('validateNumberMin');
            $symbol = sprintf($symbol, $min);
        } else $symbol = Yii::$app->sysLanguage->getTranslateBySymbol('validateNumber');
        $item['message'] = $symbol;
    }

    public static function required(&$item){
        $item['message'] = Yii::$app->sysLanguage->getTranslateBySymbol('validateRequired');
    }

    public static function string(&$item){
        $max = isset($item['max']) ?? false;
        $min = isset($item['min']) ?? false;
        if(isset($item['length'])){
            $min = isset($item['length'][0]) ?? false;
            $max = isset($item['length'][1]) ?? false;
        }

        if(false !== $max && false !== $min){
            $symbol = Yii::$app->sysLanguage->getTranslateBySymbol('validateStringInteval');
            $symbol = sprintf($symbol, $min, $max);
        } elseif(false !== $max){
            $symbol = Yii::$app->sysLanguage->getTranslateBySymbol('validateStringMax');
            $symbol = sprintf($symbol, $max);
        } elseif(false !== $min){
            $symbol = Yii::$app->sysLanguage->getTranslateBySymbol('validateStringMin');
            $symbol = sprintf($symbol, $min);
        } else $symbol = Yii::$app->sysLanguage->getTranslateBySymbol('validateString');
        $item['message'] = $symbol;
    }

    public static function unique(&$item){
        $item['message'] = Yii::$app->sysLanguage->getTranslateBySymbol('validateUnique');
    }

    public static function url(&$item){
        $item['message'] = Yii::$app->sysLanguage->getTranslateBySymbol('validateUrl');
    }

    public static function integer(&$item){
        $max = isset($item['max']) ?? false;
        $min = isset($item['min']) ?? false;
        if(false !== $max && false !== $min){
            $symbol = Yii::$app->sysLanguage->getTranslateBySymbol('validateIntegerInteval');
            $symbol = sprintf($symbol, $min, $max);
        } elseif(false !== $max){
            $symbol = Yii::$app->sysLanguage->getTranslateBySymbol('validateIntegerMax');
            $symbol = sprintf($symbol, $max);
        } elseif(false !== $min){
            $symbol = Yii::$app->sysLanguage->getTranslateBySymbol('validateIntegerMin');
            $symbol = sprintf($symbol, $min);
        } else $symbol = Yii::$app->sysLanguage->getTranslateBySymbol('validateInteger');
        $item['message'] = $symbol;
    }
}
