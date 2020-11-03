<?php
use yii\helpers\Html;
use \yii\helpers\Url;
use app\widget\AdminList;
$urlPrefix = Yii::$app->sysPath->resourcePath;
$staticResourcePrefix = "{$urlPrefix}assets/waf/";?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>FW</title>

    <?=AdminList::widget(['type' => 'common-css'])?>
    <?=AdminList::widget(['type' => 'common-js'])?>

    <!--check start-->
    <link rel="stylesheet" href="<?=$staticResourcePrefix?>js/lib/jQuery_check/css/validationEngine.jquery.css" type="text/css"/>
    <script src="<?=$staticResourcePrefix?>js/lib/jQuery_check/js/jquery.validationEngine.js" type="text/javascript" charset="utf-8"></script>
    <script src="<?=$staticResourcePrefix?>js/lib/jQuery_check/js/languages/jquery.validationEngine-zh_CN.js" type="text/javascript" charset="utf-8"></script>
    <!--check end-->

    <style type="text/css">
        .bt_qyan, .bt_tyan{margin-top:3px;}
        .btn_ref{margin-top:-8px;margin-left: 20px;}
        .server_table tbody tr:nth-child(even) td {background: #F5F5F5;}
    </style>
    <style>html{overflow-y:auto;}</style>

</head>
<body>
<div class="openWin" >

    <h1>开启云防护（云联动功能,对来自云防线节点的流量进行特殊处理，避免触发流量攻击防护策略）</h1>
    <div class="jbxx sj">

        <div class="btn_box">
            <div class="btn_list">
                <label>云联动：</label><button type="button" id="status" class="qt" onclick="statusChange(this);"></button>
                <button type="button" class="btn c_b btn_ref" title="更新节点" onclick="update()">更新节点</button>
            </div>
        </div>

        <table id="cluedfenceTable" style="display: none" width="80%" border="0" cellpadding="0" cellspacing="0" class="server_table">
            <thead>
            <tr>
                <td width="50%" class="tdbg">云防线节点名称</td>
                <td width="49%" class="tdbg">节点IP</td>
            </tr>
            </thead>
            <tbody id="hosts">
            <tr>
                <td>02_DX_WS_TJ_42.81.40.98</td>
                <td>42.81.40.98</td>
            </tr>
            <tr>
                <td>02_DX_WS_TJ_42.81.40.98</td>
                <td>42.81.40.98</td>
            </tr>
            </tbody>
        </table>

    </div>

</div>
<script type="text/javascript">
    var hosts = [
        ['02_DX_WS_TJ_42.81.40.98', '42.81.40.98'],
        ['02_DX_WS_TJ_60.28.13.139', '60.28.13.139'],
        ['03_DX_WS_CD_182.140.142.75', '182.140.142.75'],
        ['04_DX_WS_XN_210.192.118.41', '210.192.118.41'],
        ['05_DX_WS_GZ_61.145.116.30', '61.145.116.30'],
        ['06_DX_WS_FS_121.9.242.31', '121.9.242.31'],
        ['06_DX_WS_FS_122.13.168.14', '122.13.168.14'],
        ['07_DX_WS_SH_101.227.68.52', '101.227.68.52'],
        ['08_DX_GX_GZ_183.63.252.132', '183.63.252.132'],
        ['09_BGP_WS_BJ_123.103.23.145', '123.103.23.145'],
        ['21_BGP_RJ_ZS_121.201.72.254', '121.201.72.254'],
        ['22_BGP_RJ_GZ_121.201.20.213', '121.201.20.213'],
        ['23_BGP_RJ_GZ_121.201.20.212', '121.201.20.212'],
        ['24_BGP_RJ_SZ_121.201.40.167', '121.201.40.167'],
        ['25_BGP_RJ_CZ_112.73.76.37', '112.73.76.37'],
        ['26_BGP_RJ_BJ_210.73.210.230', '210.73.210.230'],
        ['27_BGP_RJ_BJ_210.73.210.231', '210.73.210.231'],
        ['28_DX_WS_YN_116.55.231.164', '116.55.231.164'],
        ['29_DX-GF_WS_XN_117.23.56.34', '117.23.56.34'],
        ['30_DX_WS_HN_124.232.151.102', '124.232.151.102'],
        ['31_BGP_GS_GZ_114.67.50.15', '114.67.50.15'],
        ['32_BGP_GS_SZ_120.132.125.50', '120.132.125.50'],
        ['33_BGP_HLT_GZ_114.67.60.35', '114.67.60.35'],
        ['34_BGP_HLT_GZ_114.67.60.34', '114.67.60.34'],
        ['35_BGP_HLT_SZ_43.247.69.115', '43.247.69.115'],
        ['36_BGP_HLT_GZ_114.67.60.36', '114.67.60.36'],
    ];

    var config = <?=json_encode($config)?>;
    $(function(){
        if(1 == config.init) $('#cluedfenceTable').show();
        else $('#cluedfenceTable').hide();

        if(1 == config.status) $('#status').addClass('bt_qyan');
        else $('#status').addClass('bt_tyan');

        var html = '';
        for(var item in hosts){
            html += '<tr><td>' + hosts[item][0] + '</td><td>' + hosts[item][1] + '</td></tr>';
        }
        $('#hosts').html(html);
    });

    function update(){
        art.dialog({
            content: '正在获取云防线节点信息',
            icon: 'loading.gif',
            time: 3
        });
    }

    // 启用、停用
    function statusChange(obj){
        var obj = $(obj);
        var status = obj.hasClass('bt_qyan') ? 1 : 0;
        if(1 == status){
            $.Layer.confirm({
                msg: '是否停用云联动功能？', fn: function () {
                    obj.addClass('bt_tyan').removeClass('bt_qyan');
                    obj.attr('title','停用');
                    updateConfig(status);
                }
            });
            //$('#cluedfenceTable').hide();
        }else{
            $.Layer.confirm({
                msg: '启用云联动，需先把网站接入云防线，具体访问云防线官方网站 http//www.cloudfence.cn', fn: function () {
                    update();
                    setTimeout("$('#cluedfenceTable').show();", 3000);
                    obj.addClass('bt_qyan').removeClass('bt_tyan');
                    obj.attr('title','启用');
                    updateConfig(status);
                }
            });
        }
    };

    function updateConfig(status){
        $.ajax({
            url: '<?=Url::to(['', 'op' => 'updateConfig'])?>',
            type: 'POST',
            data: {status: status == 1 ? 0 : 1, _csrf: $('meta[name=csrf-token]').attr('content')},
            dataType: 'json',
            timeout: 10000,//1000毫秒后超时
            cache: false,//不缓存数据
            async: false,//同步：false,异步：true,默认true
            success: function(data){

            },
        });
    }
</script>
</body>
</html>

