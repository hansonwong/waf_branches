<style type="text/css">
    html {
        height: 100%;
        background: #fafafa;
    }
</style>
</head>
<body>
<div class="openWin">
    <form action="" method="POST" id="form_id" name="form1">
        <input type="hidden" name="_csrf" id="_csrf" value="" />
        <input type="hidden" name="id" value="<?=$model->id ?>" />
        <table cellpadding="0" cellspacing="0" class="selbox">
            <tr>
                <td colspan="3" valign="top" style="padding-left:32px;">
                    <!--桥接口名称-->
                    <?=Yii::$app->sysLanguage->getTranslateBySymbol('bridgeInterfaceName') ?> ：bridge
                    <input type="text" name="TbBridgeDevice[sBridgeName]" class="validate[required,custom[integer],min[0],max[255]] text"
                                         value="<?=$model->sBridgeName ?>" placeholder="<?=Yii::$app->sysLanguage->getTranslateBySymbol('suchAs') ?>：1，2"><!--如：1，2-->
                </td>
            </tr>
            <tr>
                <td width="150" valign="top">
                    <table width="150" class="seltab">
                        <tr>
                            <th align="center"><?=Yii::$app->sysLanguage->getTranslateBySymbol('selectbindingDeviceList') ?></th><!--可选绑定设备列表-->
                        </tr>
                        <tr>
                            <td align="center" bgcolor="#FFFFFF">
                                <select name="sel_place1" size="10" multiple="multiple" id="sel_place1" style="width:150px; height:150px; ">
                                    <?php foreach( $netPortModel as $v ): ?>
                                        <option value="<?=$v['sPortName'] ?>"><?=$v['sLan'] ?></option>
                                    <?php endforeach; ?>
                                </select>
                            </td>
                        </tr>
                    </table>
                </td>
                <td align="center" valign="center" height="200">
                    <input class="selbutright" name="sure2" type="button" id="sure2"
                           onclick="allsel(document.form1.sel_place1,document.form1.sel_place2);"/>
                    <input class="selbutleft" name="sure1" type="button" id="sure1"
                           onclick="allsel(document.form1.sel_place2,document.form1.sel_place1);"/>
                </td>
                <td width="150" valign="top">
                    <table width="150" border="0" class="seltab">
                        <tr>
                            <th align="center"><?=Yii::$app->sysLanguage->getTranslateBySymbol('bindingDeviceList') ?></th><!--绑定设备列表-->
                        </tr>
                        <tr>
                            <td align="center" bgcolor="#FFFFFF">
                                <input type="hidden" name="TbBridgeDevice[sBindDevices]" id="sBindDevices" value="<?=implode(",", $model->sBindDevices); ?>">
                                <select name="sel_place2" size="10" multiple="multiple" id="sel_place2" style="width:150px; height:150px;">
                                    <?php foreach( $model->sBindDevices as $v ): ?>
                                        <option value="<?=$v ?>"><?=$v ?></option>
                                    <?php endforeach; ?>
                                </select>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        <div class="addlist-data">
            <div class="addlist-tab mar_top">
                <ul>
                    <li class="addsel"><a href="#ipv4">IPV4</a></li>
                    <li><a href="#ipv6">IPV6</a></li>
                </ul>
            </div>
            <div class="sl-content" style=" width:392px; height:155px; overflow: hidden;">
                <div id="ipv4">
                    <table width="100%" border="0" cellpadding="0" cellspacing="0" class="date_add_table">
                        <tr>
                            <td align="right"><?=Yii::$app->sysLanguage->getTranslateBySymbol('ipAddress') ?>：</td><!--IP地址-->
                            <td>
                                <textarea rows="3" style="height: auto;width:280px" class="text" name="TbBridgeDevice[sIPV4]" id="sIPV4"><?=$model->sIPV4 ?></textarea>
                            </td>
                        </tr>
                        <tr>
                            <td colspan="2">
                                <p color="gray" style="padding-left: 10px"><?=Yii::$app->sysLanguage->getTranslateBySymbol('format') ?>：192.168.2.3/255.255.255.0<?=Yii::$app->sysLanguage->getTranslateBySymbol('or') ?>192.168.2.3/24</p><!--格式：192.168.2.3/255.255.255.0或192.168.2.3/24-->
                                <p color="gray" style="padding-left: 10px"><?=Yii::$app->sysLanguage->getTranslateBySymbol('moreThanOneIpWithMultipleRow') ?></p><!--多个IP请分行填写-->
                            </td>
                        </tr>
                    </table>
                </div>
                <div style="height: 20px;"></div>
                <div id="ipv6" style="height: 155px;">
                    <table width="100%" border="0" cellpadding="0" cellspacing="0" class="date_add_table">
                        <tr>
                            <td align="right"><?=Yii::$app->sysLanguage->getTranslateBySymbol('ipAddress') ?>：</td><!--IP地址-->
                            <td>
                                <textarea class="text" rows="3" style="height: auto;width:280px" name="TbBridgeDevice[sIPV6]" id="sIPV6"><?=$model->sIPV6 ?></textarea>&nbsp;&nbsp;
                            </td>
                        </tr>
                        <tr>
                            <td colspan="2">
                                <p color="gray" style="padding-left: 10px"><?=Yii::$app->sysLanguage->getTranslateBySymbol('format') ?>:  FE80::1/64  <?=Yii::$app->sysLanguage->getTranslateBySymbol('moreThanOneIpWithMultipleRow') ?></p><!--格式:  FE80::1/64  多个IP请分行填写-->
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>
        <table cellpadding="0" cellspacing="0"  class="selbox" style="width:400px;">
            <tr>
                <td colspan="3" valign="top">
                    <table  width="100%" border="0" cellpadding="0" cellspacing="0">
                        <tr>
                            <td align="left">
                                <label style=" padding-left:6px;">
                                    <input name="TbBridgeDevice[iWeb]" id="iWeb" type="checkbox" value="1" onclick="logopen()"
                                           <?php if ($model->iWeb == 1): ?>checked<?php endif ?>/> WEBUI
                                </label>
                            </td>
                            <td align="left">
                                <label>
                                    <input name="TbBridgeDevice[iSSH]" id="iSSH" type="checkbox" value="1" onclick="logopen()"
                                           <?php if ($model->iSSH == 1): ?>checked<?php endif ?>/> SSH
                                </label>
                            </td>
                            <td align="left">
                                <label>
                                    <input name="TbBridgeDevice[iAllowPing]" id="iAllowPing" type="checkbox" value="1"
                                           <?php if ($model->iAllowPing == 1): ?>checked<?php endif ?>/>&nbsp;<?=Yii::$app->sysLanguage->getTranslateBySymbol('allow') ?>PING<!--允许-->
                                </label>
                            </td>
                            <td align="left">
                                <label>
                                    <input name="TbBridgeDevice[iAllowTraceRoute]" id="iAllowTraceRoute" type="checkbox" value="1"
                                           <?php if ($model->iAllowTraceRoute == 1): ?>checked<?php endif ?>/>&nbsp;<?=Yii::$app->sysLanguage->getTranslateBySymbol('allow') ?>Traceroute<!--允许-->
                                </label>
                            </td>
                            <td align="left">
                                <label id="iAllowLog_label">
                                    <input name="TbBridgeDevice[iAllowLog]" id="iAllowLog" type="checkbox" value="1" title="如果不用点，必须WEBUI，SSH任意选中"
                                           <?php if ($model->iAllowLog == 1): ?>checked<?php endif ?> disabled/> <?=Yii::$app->sysLanguage->getTranslateBySymbol('log') ?><!--日志-->
                                </label>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </form>
    <div style="height: 15px"></div>
</div>
<script language="javascript">
    ;(function ($) {
        var _csrf = $('meta[name=csrf-token]').attr('content');
        $('#_csrf').val(_csrf);

        $(function () {
            var dialog = top.getDialog();
            dialog.DOM.wrap.on('ok', function (e) {
                e.preventDefault();
                $("#form_id").submit();
            });

            $("#form_id").validationEngine({
                promptPosition: 'centerRight: 0, -4', scroll: false, binded: false, 'custom_error_messages': {
                    'required': {
                        'message': "* <?=Yii::$app->sysLanguage->getTranslateBySymbol('smartBlockConfigTips') ?>！" //以上各项请按需求填写
                    }
                },
                ajaxFormValidationMethod: 'post',
                //指定使用Ajax模式提交表单处理
                ajaxFormValidation: true,
                onAjaxFormComplete: function(status, form, json, options){
                    dialog.hGrid.reload();
                    if(json.code === 'T')
                    {
                        art.dialog({icon: 'succeed', content: json.info, time: 1});

                        var timeout = setTimeout(function(){
                            dialog.close();
                            clearTimeout(timeout);
                        },1000);
                    }
                    else
                    {
                        art.dialog({icon: 'error', content: json.info, time: 2});
                    }
                }
            });

        });

        //新增任务菜单切换
        $(".addlist-tab ul li").click(function () {
            $(".addlist-tab ul li").removeClass();
            $(this).addClass("addsel");
        })
    })(jQuery);

    // 向 绑定设备列表 添加
    function allsel(n1,n2)
    {
        while( n1.selectedIndex!=-1 )
        {
            var indx=n1.selectedIndex;
            var tValue=n1.options[indx].value;
            var tText =n1.options[indx].text;
            n2.options.add(new Option(tText ,tValue));
            n1.remove(indx);
        }
        //赋值给隐藏域
        var deivces='';
        $("#sel_place2 option").each(function(i,opt){
            deivces+=opt.value+',';
        });
        if(deivces!=''){
            deivces=deivces.substr(0,deivces.length-1);
        }
        $("#sBindDevices").val(deivces);
    }

    // 控制 日志 是否能被选
    function logopen(){
        var iWeb = $("#iWeb").prop("checked");
        var iSSH = $("#iSSH").prop("checked");
        var isiAllowPing = $("#iAllowPing").prop("checked");
        if (iWeb == true||iSSH == true||isiAllowPing==true) {
            $("#iAllowLog").removeAttr('disabled');
        }
        else{
            $("#iAllowLog").attr('disabled','disabled');
        }
    }
</script>