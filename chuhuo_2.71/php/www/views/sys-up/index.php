<?php
use \yii\helpers\Url;
use yii\helpers\Html;
use yii\widgets\ActiveForm;
$translate = Yii::$app->sysLanguage;
$urlPrefix = Yii::$app->sysPath->resourcePath;
?>
<style>
    .seaBox {
        display: none;
    }
</style>
<script src="<?=$urlPrefix?>assets/js/pwd.js"></script>
<script src="<?=$urlPrefix?>assets/waf/js/lib/ajaxfileupload/ajaxfileupload.js"></script>
<div class="openWin" style="height: 630px; overflow: auto;">
    <form action="" method="post" id="form_update" enctype="multipart/form-data">
        <h1 class="font-weight">系统升级</h1>
        <div class="jbxx sj">
            <table style="width:100%" border="0" cellpadding="0" cellspacing="0" class="date_add_table">
                <tr>
                    <td width="150" >
                        <label for="fLocalFile">选择系统升级包：</label>
                    </td>
                    <td>
                        <input name="fLocalFile" type="text" readonly class="input_text_wid validate[condRequired[iType1]]" id="fLocalFile" />
                        <input type="button" class="btn_ty"  value="浏览" />
                        <input class="input_file" size="30" name="recovery_file" id="recovery_file" type="file" onchange="document.getElementById('fLocalFile').value=this.value" />
                    </td>
                </tr>
                <tr>
                    <td width="150">
                        <label for="sPass">升级密码:</label>
                    </td>
                    <td>
                        <input name="sPass" id="sPass" type="password" class="text" value="" />
                        <span class="gray"></span>
                    </td>
                </tr>
                <tr>
                    <td align="right">&nbsp;</td>
                    <td><input type="button" id="btnUpdate" value="升级" class="btn_ty"/></td>
                </tr>
            </table>
        </div>
    </form>
    <form action="" method="post" id="form_return" enctype="multipart/form-data">
        <h1 class="font-weight">系统还原</h1>
        <div class="jbxx sj">
            <table style="width:100%" border="0" cellpadding="0" cellspacing="0" class="date_add_table">
                <tr>
                    <td width="150">
                        <label for="sReturnPass">还原密码:</label>
                    </td>
                    <td>
                        <input id="sReturnPass" name="sReturnPass" type="password" class="text" value="" />
                        <span class="gray"></span>
                    </td>
                </tr>
                <tr>
                    <td width="150">
                        <label>还原至升级前的系统</label>
                    </td>
                    <td>
                        <input type="button" id="btnReturn" value="还原" class="btn_ty"/>
                    </td>
                </tr>
            </table>
        </div>
    </form>
    <form action="" method="post" id="" enctype="multipart/form-data">
        <h1 class="font-weight">升级记录</h1>
        <div class="jbxx">
            <div id="maingrid"  class="list"></div>
        </div>
    </form>
</div>
<script type="text/javascript">
    (function ($) {  //避免全局依赖,避免第三方破坏
        $(document).ready(function () {
            var _csrf = $('meta[name=csrf-token]').attr('content');
            /*调用*/
            var GridTable = $.BDGrid({
                _csrf: _csrf,
                sColumnsUrl: "<?=Url::to(['config', 'op' => 'header']);?>",
                ajax: {
                    url: "<?=Url::to(['config', 'op' => 'body']);?>",
                    type: 'POST',
                    parms: {_csrf:_csrf} // yii2需要传的参数
                },
                el: '#maingrid',
                dataAction: 'server',
                showSitting: false,//是否需要操作列
                showEdit: false,
                showView: false,
                showDel: false,
                showLock: false,//是否需要解锁和锁定状态栏
                isSelectR: true,//复选按钮是否选中
                showOpen:false,//是否需要启停状态栏
                showSetting:true, //是否显示配置按钮
                allowHideColumn: false, //是否显示'切换列层'按钮
                root: 'data',//数据
                pageParmName:'page',//页码
                pagesizeParmName:'pagesize',//页数据量
                record: 'total',//总数
                width: '99.8%',
                height: '99.8%',
                pageSize: 20,
                pageSizeOptions: [10, 20, 30, 40, 50, 100],
                showRuning: false,
                checkbox: false,
                columnDefs: [
                ]
            });

        });
    })(jQuery);

    //升级
    $("#btnUpdate").click(function()
    {
        var _csrf = $('meta[name=csrf-token]').attr('content');
        var sFile = $("#fLocalFile").val();
        var sPass = $("input[name=sPass]").val();

        if( sFile.trim().length<1 )
        {
            $.Layer.alert({msg:"请选择文件！"});
            return;
        }
        if( sPass.trim().length<1 )
        {
            $.Layer.alert({msg:"请输入密码！"});
            return;
        }

        sPass = authcode(sPass,'ENCODE','bluedon_edu');
        $.Layer.confirm({
            msg: '升级之前确保已经备份数据 , 升级过程中将不允许做任何操作', fn: function () {
                $.ajaxFileUpload ({
                    url: "<?=Url::to(['config', 'op' => 'up']);?>",
                    secureuri:"updateFrame", //与页面处理代码中file相对应的ID值
                    fileElementId:['recovery_file'],
                    dataType: 'json', //返回数据类型:text，xml，json，html,scritp,jsonp五种
                    data :{_csrf:_csrf, sPass:sPass},
                    async:false,
                    success: function (data) {
                        if(data.code!=='T')
                        {
                            $.Layer.alert({
                                title: '系统友情提示', msg: data.info, fn: function () {
                                    $("#fLocalFile").val('');
                                    $("input[name=sPass]").val('');
                                }
                            });
                        }

                        var dialog = $.Layer.iframe(
                            {
                                title: '系统升级',
                                url: "<?=Url::to(['config', 'op' => 'Loading']);?>"+'&pre_name='+data.pre_name,
                                width: 600,
                                height: 280,
                                cancel:false,
                                button:false
                            });
                    },
                    error: function () {
                        $.Layer.alert({
                            title: '系统友情提示', msg: '升级失败', fn: function () {
                                $("#fLocalFile").val('');
                                $("input[name=sPass]").val('');
                            }
                        });
                    }
                });
            }
        })
    });

    //还原
    $("#btnReturn").click(function()
    {
        var _csrf = $('meta[name=csrf-token]').attr('content');

        var sPass = $("input[name=sReturnPass]").val();
        if( sPass === '' )
        {
            $.Layer.alert({msg:"请输入密码！"});
            return;
        }

        sPass = authcode(sPass,'ENCODE','bluedon_edu');
        $.Layer.confirm({
            msg: '是否确定进行系统还原操作', fn: function () {
                $.ajax({
                    url  : "<?=Url::to(['config', 'op' => 'returnSystem']);?>",
                    type : 'POST',
                    async: false,
                    dataType: 'json',
                    data :{_csrf:_csrf, sPass:sPass},
                    success: function (data) {
                        if( data.code !== 'T' )
                        {
                            $.Layer.alert({
                                title: '系统友情提示', msg: data.info, fn: function () {
                                    $("input[name=sReturnPass]").val('');
                                }
                            });
                        }

                        var dialog = $.Layer.iframe(
                            {
                                title: '系统还原',
                                url: "<?=Url::to(['config', 'op' => 'returnLoading']);?>",
                                width: 600,
                                height: 280,
                                cancel:false,
                                button:false
                            });
                    },
                    error: function ()
                    {
                        $.Layer.alert({
                            title: '系统友情提示', msg: '还原失败', fn: function () {
                                $("input[name=sReturnPass]").val('');
                            }
                        });
                    }
                });
            }
        });
    });
</script>
						
