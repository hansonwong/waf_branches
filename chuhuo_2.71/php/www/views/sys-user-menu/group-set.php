<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
<?php
use \yii\helpers\Url;
use yii\helpers\Html;
use app\widget\AdminList;
$urlPrefix = Yii::$app->sysPath->resourcePath;
$staticResourcePrefix = "{$urlPrefix}assets/waf/";?>
    <meta charset="utf-8">
    <meta name="renderer" content="webkit|ie-comp|ie-stand">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <meta name="viewport" content="width=device-width,initial-scale=1,minimum-scale=1.0,maximum-scale=1.0,user-scalable=no" />
    <meta http-equiv="Cache-Control" content="no-siteapp" />
    <?=Html::csrfMetaTags()?>
    <LINK rel="Bookmark" href="<?=$urlPrefix?>favicon.ico" >
    <LINK rel="Shortcut Icon" href="<?=$urlPrefix?>favicon.ico" />
    <!--[if lt IE 9]>
    <script type="text/javascript" src="<?=$urlPrefix?>assets/h-ui/lib/html5.js"></script>
    <script type="text/javascript" src="<?=$urlPrefix?>assets/h-ui/lib/respond.min.js"></script>
    <script type="text/javascript" src="<?=$urlPrefix?>assets/h-ui/lib/PIE_IE678.js"></script>
    <![endif]-->

    <!--公共-->
    <link href="<?=$staticResourcePrefix?>skin/blue/style/public.css" rel="stylesheet" type="text/css">
    <link href="<?=$staticResourcePrefix?>skin/blue/style/style.css" rel="stylesheet" type="text/css">
    <link href="<?=$staticResourcePrefix?>skin/blue/style/style_waf.css" rel="stylesheet" type="text/css">

    <link rel="stylesheet" type="text/css" href="<?=$urlPrefix?>assets/h-ui/static/h-ui/css/H-ui.min.css" />
    <link rel="stylesheet" type="text/css" href="<?=$urlPrefix?>assets/h-ui/static/h-ui.admin/css/H-ui.admin.css" />
    <link rel="stylesheet" type="text/css" href="<?=$urlPrefix?>assets/h-ui/lib/Hui-iconfont/1.0.7/iconfont.css" />
    <link rel="stylesheet" type="text/css" href="<?=$urlPrefix?>assets/h-ui/lib/icheck/icheck.css" />
    <link rel="stylesheet" type="text/css" href="<?=$urlPrefix?>assets/h-ui/static/h-ui.admin/skin/default/skin.css" id="skin" />
    <link rel="stylesheet" type="text/css" href="<?=$urlPrefix?>assets/h-ui/static/h-ui.admin/css/style.css" />
    <!--[if IE 6]>
    <script type="text/javascript" src="<?=$urlPrefix?>assets/h-ui/lib/DD_belatedPNG_0.0.8a-min.js" ></script>
    <script>DD_belatedPNG.fix('*');</script>
    <![endif]-->
    <script src="<?=$urlPrefix?>assets/h-ui/lib/jquery/1.9.1/jquery.min.js"></script>


    <script src="<?=$urlPrefix?>assets/h-ui/lib/layer/2.1/layer.js"></script>
    <!--<script src="<?=$urlPrefix?>assets/h-ui/lib/laypage/1.2/laypage.js"></script>-->
    <!--<script src="<?=$urlPrefix?>assets/h-ui/lib/My97DatePicker/WdatePicker.js"></script>-->
    <script src="<?=$urlPrefix?>assets/h-ui/static/h-ui/js/H-ui.js"></script>
    <script src="<?=$urlPrefix?>assets/h-ui/static/h-ui.admin/js/H-ui.admin.js"></script>

    <script src="<?=$urlPrefix?>assets/h-ui/lib/bootstrap-modal/2.2.4/bootstrap-modalmanager.js"></script>
    <script src="<?=$urlPrefix?>assets/h-ui/lib/bootstrap-modal/2.2.4/bootstrap-modal.js"></script>

<link rel="StyleSheet" href="<?=$urlPrefix?>assets/js/dtree/dtree.css" type="text/css" />
<script>var dtreeImgPath = '<?=$urlPrefix?>assets/js/dtree/img/';</script>
<script src="<?=$urlPrefix?>assets/js/dtree/dtree.js"></script>

<script src="<?=$urlPrefix?>assets/js/common.js"></script>
</head>
<body>
<div class="page-container">
    <div class="row cl">
        <div class="col-xs-12 col-sm-12">
            <a class="btn btn-success" href="javascript: d.openAll();"><?=Yii::$app->sysLanguage->getTranslateBySymbol('allExpand')?></a>
            <a class="btn btn-success" href="javascript: d.closeAll();"><?=Yii::$app->sysLanguage->getTranslateBySymbol('allExpandOff')?></a>
            <a class="btn btn-success" href="javascript:location.replace(location.href);" title="刷新" ><i class="Hui-iconfont">&#xe68f;</i></a>
        </div>
    </div>

    <div class="row cl">
        <div class="dtree container">
            <div class="col-xs-12 col-sm-12"><br>
                <script>
                    var menu = authority = null;
                    <?="menu = ".json_encode($menu).";authority = ".json_encode($authority).";"?>
                    var yesImg = '<?=$urlPrefix?>assets/js/dtree/img/yes.png';
                    var noImg = '<?=$urlPrefix?>assets/js/dtree/img/no.png';

                    var d = new dTree('d');
                    d.add(0,-1, 'TOP', 'javascript:;');
                    <?php
                    foreach($menu as $item){
                        echo "d.add({$item['id']}, {$item['parent_id']}, '{$item['name']}<span><img></span>',".
					        "'javascript:operation({$item['id']});',".
					        "{$item['id']});";
                    }
                    ?>
                    document.write(d);
                </script>
            </div>
        </div>
    </div>
</div>
</body>
<style>
    .dtree .dTreeNode a>span>img{width:16px;}
</style>
<script>

    $(function(){
        $('[name=_csrf]').val($('meta[name=csrf-token]').attr('content'));
        $.Huitab("#tab_demo .tabBar span","#tab_demo .tabCon","current","click","0");

        $(function(){
            for(var menuItem in menu){
                var item = menu[menuItem];
                //$('[title=' + item.id + ']').attr('href', 'javascript:operation(' + item.id + ');');
                $('[title=' + item.id + '] span>img').attr('src', noImg);
            }

            for(var menuId in authority){
                var item = authority[menuId];
                $('[title=' + item.sys_menu_id + '] span>img').attr('src', (1 == item.enable) ? yesImg : noImg);
                $('[title=' + item.sys_menu_id + ']').attr('authorityId', item.id);
            }
        });
    });
    function operation(id){
        var obj = $('[title=' + id + ']');
        var authorityId = obj.attr('authorityId');
        if(undefined == authorityId) authorityId = 0;

        $.ajax({
            url: '<?=Url::to(['authority-modify'])?>&id=' + authorityId,
            type: 'POST',
            data: {
                menuId : id,
                groupId : "<?=$groupId?>",
                _csrf   : $('meta[name=csrf-token]').attr('content'),
            },
            dataType: 'json',
            timeout: 5000,//1000毫秒后超时
            cache: false,//不缓存数据
            async: false,//同步：false,异步：true,默认true
            success: function(data){
                switch(data.success){
                    case true:
                        var icon = (1 == data.data.sym) ? yesImg : noImg;
                        $('[title=' + id + '] span>img').attr('src', icon);
                        break;
                    case false:
                        alert('<?=Yii::$app->sysLanguage->getTranslateBySymbol('requestFailed')?>');
                        break;
                    default :;
                }
            },//请求成功后执行
            error: function(){
                alert('<?=Yii::$app->sysLanguage->getTranslateBySymbol('networkTimeout')?>');
            }
        });
    }
</script>
</html>