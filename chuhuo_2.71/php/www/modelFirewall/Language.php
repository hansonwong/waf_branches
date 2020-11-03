<?php

namespace app\modelFirewall;

use Yii;

class Language extends \app\logic\model\BaseModel
{
    public static function tableName()
    {
        return 'm_tblanguage';
    }

    public static function getDb()
    {
        return Yii::$app->get('dbFirewall');
    }

    public function rules()
    {
        return [
            [['zh_CN', 'en_US', 'fr_FR', 'de_DE', 'ja_JP', 'th_TH', 'cs_CZ', 'es_ES', 'pt_PT'], 'string', 'max' => 512],
        ];
    }

    public function attributeLabels()
    {
        return [
            'id' => 'ID',
            'zh_CN' => 'Zh  Cn',
            'en_US' => 'En  Us',
            'fr_FR' => 'Fr  Fr',
            'de_DE' => 'De  De',
            'ja_JP' => 'Ja  Jp',
            'th_TH' => 'Th  Th',
            'cs_CZ' => 'Cs  Cz',
            'es_ES' => 'Es  Es',
            'pt_PT' => 'Pt  Pt',
        ];
    }

    public static function syncFirewallTranslation(){
        $result = [];
        $translation = function($keys, &$result){
            $translate = Yii::$app->sysLanguage;
            foreach ($keys as $v){
                $result[] = [
                    'zh_CN' => $translate->getTranslateBySymbolWithSourceLanguage($v),
                    'en_US' => $translate->getTranslateBySymbolWithAssignLanguage($v, 'en-US')];
            }
        };

        #登录
        $tKey = ['verificationCodeError', 'invalidUser', 'passwordError', 'userLoginBlock', 'loginFailed'];
        $translation($tKey, $result);

        #操作
        $tKey = ['see', 'config', 'create', 'update', 'delete', 'export', 'import'];
        $translation($tKey, $result);

        #菜单
        $menus = \app\models\SysUserMenu::find()->select(['id', 'name'])->asArray()->all();
        $tKey = [];
        foreach ($menus as $menu) $tKey[] = $menu['name'];
        $tKey = array_unique($tKey);
        $translation($tKey, $result);

        $all = self::find()->asArray()->all();
        $allKey = [];
        foreach ($all as $item) $allKey[] = $item['zh_CN'];
        $allKey = array_unique($allKey);

        #同步
        $transaction = Yii::$app->dbFirewall->beginTransaction();
        try {
            $model = new self;
            foreach ($result as $data){
                if(in_array($data['zh_CN'], $allKey)) continue;
                $model->isNewRecord = true;
                $model->setAttributes($data);
                $model->save();
                $model->id = 0;
            }
            $transaction->commit();
        } catch (Exception $e) {
            $transaction->rollBack();
        }
        return true;
    }
}
