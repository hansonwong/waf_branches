<?php

namespace app\assets;

use yii\web\AssetBundle;

/**
 * Main frontend application asset bundle.
 */
class AppAsset extends AssetBundle
{
    public $basePath = '@webroot';
    public $baseUrl = '@web';
    public $css = [
        'assets/waf/skin/blue/style/public.css',
        'assets/waf/skin/blue/style/style.css',
        'assets/waf/skin/blue/style/style_waf.css',
        //grid
        'assets/waf/js/lib/ligerUI/css/ligerui-all.css',
        //check
        'assets/waf/js/lib/jQuery_check/css/validationEngine.jquery.css',

        'assets/waf/js/lib/dialog/dialog.css',
        'assets/waf/js/lib/ztree/style/zTreeStyle.css',
    ];
    public $js = [
        //'assets/waf/js/lib/baseLanguage.js',
        '/waf.php?r=language%2Flang-source-for-js&tpl=b',
        'assets/waf/js/lib/jquery.min.js',
        // grid
        'assets/waf/js/lib/ligerUI/js/base.js',
        'assets/waf/js/lib/ligerUI/js/ligerGrid.js',

        'assets/waf/js/bd/grid.js',
        // check
        'assets/waf/js/lib/jQuery_check/js/jquery.validationEngine.js',
        'assets/waf/js/lib/jQuery_check/js/languages/jquery.validationEngine-zh_CN.js',

        'assets/waf/js/lib/dialog/jquery.artDialog.source.js',
        'assets/waf/js/lib/dialog/iframeTools.source.js',

        //弹出框封装和日历的扩展
        'assets/waf/js/lib/unit.js',

        // 日历
        'assets/waf/js/lib/My97DatePicker/WdatePicker.js',

        // ztree
        'assets/waf/js/lib/ztree/js/jquery.ztree.core.js',
        'assets/waf/js/lib/ztree/js/jquery.ztree.excheck.js',

        'assets/waf/js/lib/fun.js',
    ];

    //依赖关系
    public $depends = [
        //'yii\web\YiiAsset',
        //'yii\web\JqueryAsset',
    ];

    public $jsOptions = ['position' => \yii\web\View::POS_HEAD];

    //定义按需加载JS方法
    public static function addJs($view, $jsfile) {
        $view->registerJsFile($jsfile, [AppAsset::className(), "depends" => "app\assets\AppAsset"]);
    }

    //定义按需加载css方法
    public static function addCss($view, $cssfile) {
        $view->registerCssFile($cssfile, [AppAsset::className(), "depends" => "app\assets\AppAsset"]);
    }


}