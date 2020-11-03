<?php
namespace app\models;

use Yii;
use app\logic\model\tools\SelectList;

class PasswordPolicy extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function attributeLabelsSource()
    {
        return [
            'enAlphabet' => 'englishLettersMustBeIncluded',
            'number' => 'mustContainNumbers',
            'specialChar' => 'specialCharactersMustBeIncluded',
            'modifyPwdFirst' => 'firstLoginMustChangeThePassword',
            'expirationTime' => 'longestUseNumberOfPasswords',
            'length' => 'minimumLengthOfCipher',
        ];
    }

    public function rulesSource()
	{
		return [
            [['enAlphabet', 'number', 'specialChar', 'modifyPwdFirst',], 'in', 'range' => [0,1]],
            [['expirationTime',], 'integer', 'min' => 7, 'max' => 365],
            [['length',], 'integer', 'min' => 1],
            [['expirationTime', 'length',], 'required',],
		];
	}

    public function ListField()
    {
        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'enAlphabet' => SelectList::enable('select'),
                'number' => SelectList::enable('select'),
                'specialChar' => SelectList::enable('select'),
                'modifyPwdFirst' => SelectList::enable('select'),
                #'expirationTime' => ['tipsTKey' => '0MeansThatItIsNotEffective'],
            ],
            'customStr' => false,
        ];
        return $field;
    }

    public static function validatePwd($pwd){
        $model = new self;
        $validate = $model->get(false);
        $attribute = $model->attributeLabels();

        $info = [];
        if(1 == $validate->enAlphabet){
            preg_match('/[A-Za-z]+/', $pwd, $matches, PREG_OFFSET_CAPTURE);
            if(!isset($matches[0][0])) $info[] = $attribute['enAlphabet'];
        }
        if(1 == $validate->number){
            preg_match('/\d+/', $pwd, $matches, PREG_OFFSET_CAPTURE);
            if(!isset($matches[0][0])) $info[] = $attribute['number'];
        }

        if(1 == $validate->specialChar){
            preg_match('/((?=[\x21-\x7e]+)[^A-Za-z0-9])/', $pwd, $matches, PREG_OFFSET_CAPTURE);
            if(!isset($matches[0][0])) $info[] = $attribute['specialChar'];
        }

        if($validate->length > strlen($pwd)){
            $str = Yii::$app->sysLanguage->getTranslateBySymbol('validateStringMin');
            $info[] = sprintf($str, $validate->length);
        }

        if(0 < count($info)) return implode(',', $info);
        return true;
    }
}
