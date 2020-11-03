<?php

namespace app\logic\waf\helpers;

use Yii;
use app\models\Rules;
use app\models\BaseAccessCtrl;
use app\models\RulesCustom;
use app\modelLogs\CountryCode;
use app\modelLogs\Areas;
class WafModels
{
    /**
     * 根据 攻击类型 返回攻击类型的realid
     * @param $type
     * @return mixed|string
     */
    public static function getRealIdByType($type)
    {
        if( strlen($type)<1 ) return [];

        $rst = Rules::find()->select(['realid'])->where(['type'=> $type])->asArray()->all();
        if( !empty($rst) ) return array_column($rst,'realid');

        $rst = RulesCustom::find()->select(['realid'])->where(['type'=> $type])->asArray()->all();
        if( !empty($rst) ) return array_column($rst,'realid');

        $rst = BaseAccessCtrl::find()->select(['realid'])->where(['type'=> $type])->asArray()->all();
        if( !empty($rst) ) return array_column($rst,'realid');

        return [];
    }

    /**
     * 检测 端口是否正解  80|8080|443|8088
     * @param $model object 模型
     * @param $ports string 数组
     * @return array
     */
    public static function validatePorts($model, $ports)
    {
        $data = ['code'=>'F', 'info'=>''];

        $ports =  explode("|", $ports);
        // 判断检测端口是否为空
        if( empty(array_filter($ports,'is_numeric')) )
        {
            $info = $model->attributeLabels()['ports'];
            $info .= Yii::$app->sysLanguage->getTranslateBySymbol('parameterError'); // 参数错误
            $data['info'] = $info;

            return $data;
        }

        // 判断检测输入端口是否为正整数
        foreach( $ports as $v )
        {
            if( !is_numeric($v) || intval($v)<1 || intval($v)>65535 )
            {
                $info = $model->attributeLabels()['ports'];
                $info .= Yii::$app->sysLanguage->getTranslateBySymbol('parameterError'); // 参数错误
                $data['info'] = $info;
                return $data;
            }
        }

        $data['code'] = 'T';
        $data['info'] = '成功';
        return $data;
    }

    /**
     * 获取国家地区
     * @param string $country  CN
     * @param string $province 01
     * @param string $city
     * @return string
     */
    public static function getCountry($country='', $province='', $city='')
    {
        // en-US  zh-CN 当前语言
        $lang = Yii::$app->sysLanguage->getLanguage();

        // 国家
        $country = strlen($country)<1 ?'CN' : trim($country);
        $countryCodeModel = CountryCode::find()->select(['EnCountry', 'CnCountry'])->where(['CountryCode'=> $country])->asArray()->one();

        $countryStr = Yii::$app->sysLanguage->getTranslateBySymbol('unknown');
        if( !empty($countryCodeModel) )
        {
            $countryStr = $countryCodeModel['EnCountry'];
            if( $lang=='zh-CN' )
            {
                $countryStr = $countryCodeModel['CnCountry'];
            }
        }

        // 省份
        $provinceStr = Yii::$app->sysLanguage->getTranslateBySymbol('unknown');
        if( $country == 'CN' && intval($province) > 0 && $province !='unknown' )
        {
            $areasModel = Areas::find()->select(['Province', 'Desc'])->where(['Code'=> $province])->asArray()->one();
            if( !empty($countryCodeModel) )
            {
                $provinceStr = $areasModel['Province'];
                if( $lang=='zh-CN' )
                {
                    $provinceStr = substr($areasModel['Desc'], strrpos($areasModel['Desc'], ':')+1);
                }
            }
        }

        $cityStr = Yii::$app->sysLanguage->getTranslateBySymbol('unknown');
        if( strlen($city)>0 && $city !='unknown' )
        {
            $cityStr = $city;
        }

        return $countryStr.'-'.$provinceStr.'-'.$cityStr;
    }
}