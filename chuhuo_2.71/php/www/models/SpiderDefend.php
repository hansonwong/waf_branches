<?php

namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;
use app\logic\waf\models\SelectList as SL;

class SpiderDefend extends \app\logic\model\BaseConfigValidateModelForDb
{
    public function rulesSource()
    {
        return [
            [['list'], 'safe'],
        ];
    }

    public function attributeLabelsSource()
    {
        return [
            'headTitle1' => Yii::$app->sysLanguage->getTranslateBySymbol('openLater').', '.Yii::$app->sysLanguage->getTranslateBySymbol('spiderDefendList'),
            'list' => 'spiderType',
        ];
    }

    public function ListField()
    {
        $fileType = [
            'Googlebot|Adsbot' => 'spiderGoogle',#谷歌爬虫
            'baiduspider' => 'spiderBaidu',#百度爬虫
            'Yahoo!' => 'spiderYahoo',#雅虎爬虫
            'iaskspider' => 'spiderSina',#新浪爬虫

            'YodaoBot' => 'spider163',#网易爬虫
            'msnbot' => 'spiderMsn',#MSN爬虫
            'bingbot' => 'spiderBing',#必应爬虫
            'Sosospider|Sosoblogspider|Sosoimagespider' => 'spiderSoSo',#SOSO爬虫

            '360Spider' => 'spider360',#360爬虫
            'JikeSpider' => 'spiderChinaso',#即刻爬虫
            'ia_archiver' => 'Alexa',#
            'lanshanbot' => 'spiderEast',#东方网景

            'Adminrtspider' => 'spiderRetu',#热土爬虫
            'HuaweiSymantecSpider' => 'spiderHuaWei',#华为赛门铁克
            'MJ12bot' => 'spiderEnglish',#英国爬虫
            'YandexBot' => 'spiderRussia',#俄罗斯爬虫

            'Yeti' => 'spiderKorea',#韩国爬虫
            'DoCoMo' => 'spiderJanpan',#日本爬虫
            'HTTrack' => 'HTTrack',#
            'checkbox' => 'Heritrix',#

            'Datapark' => 'Datapark',
            'JSpider' => 'JSpider',
            'python' => 'python',
            'curl' => 'curl',

            'wget' => 'Wget',
            'lftp|BlackWidow|ChinaClaw|Custo|DISCo|eCatch|EirGrabber|EmailSiphon|EmailWolf|ExtractorPro|EyeNetIE|FlashGet|GetRight|GetWeb!|Go!Zilla|Go-Ahead-Got-It|GrabNet|Grafula|HMView|InterGET|JetCar|larbin|LeechFTP|Navroad|NearSite|NetAnts|NetSpider|NetZIP|Octopus|PageGrabber|pavuk|pcBrowser|RealDownload|ReGet|SiteSnagger|SmartDownload|SuperBot|SuperHTTP|Surfbot|tAkeOut|VoidEYE|WebAuto|WebCopier|WebFetch|WebLeacher|WebReaper|WebSauger|WebStripper|WebWhacker|WebZIP|Widow|WWWOFFLE|Zeus|lycos_spider_|Gaisbot|Search17Bot|crawler|MLBot|scooter|Gigabot|DotBot' => 'spiderOther',
        ];
        foreach($fileType as $k => $v){
            $fileType[$k] = Yii::$app->sysLanguage->getTranslateBySymbol($v);
        }

        $fieldKey = $this->modelName;
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'list' => [
                    'type' => 'checkbox',
                    'data' => $fileType,
                    'labelWidth' => '100px',
                    'rowStyle' => 2
                ],
            ],
        ];
        return $field;
    }

    public function afterSave(){
        Yii::$app->wafHelper->pipe("CMD_NGINX");
    }
}
