<!DOCTYPE HTML>
<html><head>
    <meta charset="UTF-8">
    <title><?php echo Yii::app()->name ?></title>
    <?php $this->renderPartial('/layouts/js_css'); ?>
    <?php $this->renderPartial('/layouts/ext_table'); ?>
    <?php $this->renderPartial('/layouts/ext_datetime'); ?>
    <?php $this->renderPartial('/layouts/ext_validation'); ?>
    <script type="text/javascript">var save_path=$.PhpUrl('Network/NetPortSave')</script>
    <script type="text/javascript" src="<?php echo Yii::app()->getTheme()->getBaseUrl()?>/js/act/common_save.js"></script>
    <style type="text/css">
        .input_ccc {background-color: #EBEBE4;}
    </style>
    <script type="text/javascript">
        $(document).ready(function() {
            //新增任务菜单切换
            $('#ipv4').show();

            $(".addlist-tab ul li").click(function(){
                $(".addlist-tab ul li").removeClass();
                $(this).addClass("addsel");
                $('#ipv4').hide();
                $('#ipv6').hide();
                $($(this).find('a').attr('href')).show();
            });

            var id=$("#id").val();
            if(id!='')
            {
                String.prototype.replaceAll = function(s1,s2) {
                    return this.replace(new RegExp(s1,"gm"),s2);
                };
                $("#sIPV4Address").val($("#sIPV4Address").val().replaceAll(",","\r\n"));
                $("#sIPV6Address").val($("#sIPV6Address").val().replaceAll(",","\r\n"));

                var dialog=top.getDialog();
                var data=dialog.hData;
                if(data.sPortName!=data.sLan)
                {
                    if(data.sLan =='' || data.sLan ==undefined){
                        $("#sLan").val(data.sPortName);
                    }else{
                        $("#sLan").val(data.sLan);
                    }
                }
                else
                {
                    $("#sLan").val(data.sLan);
                }

                if(data.sWorkMode=='mirror')
                {
                    $("#sWorkMode").append('<option value="mirror"><?=Yii::t('lang','镜像模式');?></option>');
                    $(":input[name='sWorkMode']").val('mirror');
                }
            }

            setCheck(false);

            $("#sIPV4Address").click();

            //判断是否管理口
            if(data.is_enPort==1)
            {
                $("#is_enPort").val(1);
                $("#sWorkMode").empty();

                $("#sWorkMode").prepend('<option value="route"><?=Yii::t('lang','路由模式');?></option>');
                $("#sWorkMode").append('<option value="redundancy"><?=Yii::t('lang','冗余模式');?></option>');

                $("#sWorkMode").find('option[value='+data.sWorkMode+']').attr('selected', "selected");

                if( data.sWorkMode==='route' )
                {
                    $("#iStatus").attr('disabled','disabled');
                    $("#iWeb").attr('disabled','disabled');
                    $("#iAllowPing ").prop("checked","checked").attr('disabled','disabled');
                }
            }
            else
            {
                $("#is_enPort").val(0);
            }

            if(data.iSshStatus!=undefined && data.iSshStatus==0){
                $("#iSSH").attr('disabled','disabled').removeAttr("checked");
            }

            //选择界面上的 静态与DHCP radio
            if(data.iIPV4ConnectionType=="2"){
                $(":input[name='iIPV4ConnectionType'][value='2']").prop("checked","checked");
            }else{
                $(":input[name='iIPV4ConnectionType'][value='1']").prop("checked","checked");
            }

            if(data.iIPV6ConnectionType=="2"){
                $(":input[name='iIPV6ConnectionType'][value='2']").prop("checked","checked");
            }else{
                $(":input[name='iIPV6ConnectionType'][value='1']").prop("checked","checked");
            }

            //判断是否虚拟口
            if(data.is_virth=="1"){
                $("textarea").attr("readonly", true).css("cursor", "default").addClass('input_ccc');
                $("input:radio:not(:checked)").attr("disabled","disabled");
            }
            //判断是否桥设备
            if(data.is_bridge=="1"){
                $("#iAllowFlow").attr("disabled","disabled");
                $("#iAllowLog_label").attr("disabled","disabled");
                $("#iAllowFlow_label").css('display','none');
            }

        });
        //设置工作模式
        function setCheck(chk, s=0){
            var val  = $("#sWorkMode").val();

            //判断是否管理口
            var is_enPort   = $("#is_enPort").val();

            if(val=='mirror' && chk==true)
            {
                $.Layer.alert({msg:"<?=Yii::t('lang','只能设置一个镜像模式的网口，请确认！');?>"});
            }

            if( is_enPort=== '0' )
            {
                if(val=='route'|| val =='nat')
                {
                    $("#iWeb,#iSSH,#iAllowPing,#iAllowTraceRoute,#iAllowLog").removeAttr("disabled");
                    $("#sIPV4Address,#sIPV6Address").removeAttr("disabled");
                }
                else
                {
                    $("#iWeb,#iSSH,#iAllowPing,#iAllowTraceRoute,#iAllowLog").attr({disabled:"disabled"}).removeAttr("checked");
                    $("#sIPV4Address,#sIPV6Address").attr({disabled:"disabled"}).val("");
                }
            }

            if( is_enPort=== '1' )
            {
                $("#iStatus").attr('disabled','disabled');
                if( val==='route' )
                {
                    //$("#iWeb,#iSSH,#iAllowPing,#iAllowTraceRoute,#iAllowLog").attr({disabled:"disabled"}).removeAttr("checked");


                    //$("#iAllowPing ").prop("checked","checked").attr('disabled','disabled');

                    $("#sIPV4Address,#sIPV6Address").removeAttr("disabled");
                }
                else
                {
                    if( s===1 )
                    {
                        $("#iWeb,#iSSH,#iAllowPing,#iAllowTraceRoute,#iAllowLog").removeAttr("disabled").removeAttr("checked");

                        $("#sIPV4Address,#sIPV6Address").removeAttr("disabled");
                    }
                }
            }


            if(val=='bridge' || val=='route' || val =='nat'){
                $("#iAllowFlow").removeAttr("disabled");
            }else{
                $("#iAllowFlow").attr({disabled:"disabled"}).removeAttr("checked");
            }

            //判断是否管理口
            /*if(is_enPort ==1){
                $("#iWeb,#iSSH,#iAllowPing,#iAllowTraceRoute").attr({checked:"checked"});
            }*/
        }

        function ip4type(){
            var models = $("#sWorkMode").val();
            var ipv4type = $('input[name="iIPV4ConnectionType"]:checked ').val();
            if(models =='route'){
                if(ipv4type == 2){
                    $("#sIPV4Address").attr({disabled:"disabled"}).val("");
                }else{
                    $("#sIPV4Address").removeAttr("disabled");
                }
            }
        }
        function ip6type(){
            var models = $("#sWorkMode").val();
            var ipv4type = $('input[name="iIPV6ConnectionType"]:checked ').val();
            if(models =='route'){
                if(ipv4type == 2){
                    $("#sIPV6Address").attr({disabled:"disabled"}).val("");
                }else{
                    $("#sIPV6Address").removeAttr("disabled");
                }
            }
        }
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
</head>
<body>
<div class="openWin">
    <form name="form1" method="post" action="" class="edit_form">
        <input type="hidden" name="id" id="id">
        <input type="hidden" name="is_enPort" id="is_enPort">
        <input type="hidden" name="oldWorkMode" id="oldWorkMode">
        <input type="hidden" name="enpPortName" id="enpPortName">
        <input type="hidden" name="msPortName" id="msPortName">
        <input type="hidden" name="tis_id" id="tis_id" value="<?=$tis_id;?>"/>
        <table cellpadding="0" cellspacing="0" class="selbox" style="width:460px">
            <tr>
                <td align="right"><?=Yii::t('lang','启用');?>：</td>
                <td valign="top">
                    <input type="checkbox"  name="iStatus" id="iStatus" value="1" readonly style="border:0px;">
                </td>
            </tr>
            <tr>
                <td align="right"><?=Yii::t('lang','接口名称');?>：</td>
                <td valign="top">
                    <input id="sLan" type="text"   readonly style="border:0px;">
                    <input type="hidden"  name="sPortName" readonly style="border:0px;">
                </td>
            </tr>
            <tr>
                <td align="right"><?=Yii::t('lang','网口模式');?>：</td>
                <td valign="top">
                    <input type="radio" value="1" name="sPortMode" checked><?=Yii::t('lang','内网口');?>
                    <input type="radio" value="2" name="sPortMode"><?=Yii::t('lang','外网口');?>
                </td>
            </tr>
            <tr>
                <td width="120px" align="right"><font class="red">*</font><?=Yii::t('lang','工作模式');?>：</td>
                <td valign="top">
                    <select name="sWorkMode" id="sWorkMode" onchange="setCheck(true, 1)" class="validate[required] text" style="width:150px;">
                        <option value="route"><?=Yii::t('lang','路由模式');?></option>
                        <option value="bridge"><?=Yii::t('lang','桥模式');?></option>
                        <option value="virtual"><?=Yii::t('lang','虚拟线');?></option>
						<option value="bypass"><?=Yii::t('lang','旁路模式');?></option>
                        <option value="nat"><?=Yii::t('lang','NAT模式');?></option>
                        <?php if($port ==0){?>
                            <option value="mirror"><?=Yii::t('lang','镜像模式');?></option>
                        <?php }?>
                        <option value="redundancy"><?=Yii::t('lang','冗余模式');?></option>
                    </select>
                </td>
            </tr>
            <tr>
                <td valign="top" style="padding:0px;" colspan="2">
                    <table  width="100%" border="0" cellpadding="0" cellspacing="0">
                        <tr>
                            <!-- <td align="left" ><label style=" padding-left:6px;">
                                    <input name="iByManagement" id="iByManagement" type="checkbox" value="1" onclick="logopen()" /> 用于管理
                                </label> </td> -->
                            <td align="left" ><label style=" padding-left:6px;">
                                    <input name="iWeb" id="iWeb" type="checkbox" value="1" onclick="logopen()" /> WEBUI
                                </label> </td>
                            <td align="left" ><label>
                                    <input name="iSSH" id="iSSH" type="checkbox" value="1" onclick="logopen()" /> SSH
                                </label> </td>
                            <td align="left"><label>
                                    <input name="iAllowPing" id="iAllowPing" type="checkbox" value="1" onclick="logopen()" /> <?=Yii::t('lang','允许PING');?>
                                </label></td>
                            <td align="left"><label>
                                    <input name="iAllowTraceRoute" id="iAllowTraceRoute" type="checkbox" value="1" /> <?=Yii::t('lang','允许Traceroute');?>
                                </label> </td>
                            <td align="left"><label id="iAllowFlow_label">
                                    <input name="iAllowFlow" id="iAllowFlow" type="checkbox" value="1" /> <?=Yii::t('lang','允许流控');?>
                                </label> </td>
                            <td align="left"><label id="iAllowLog_label">
                                    <input name="iAllowLog" id="iAllowLog" type="checkbox" value="1" /> <?=Yii::t('lang','日志');?>
                                </label> </td>
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

            <div class="sl-content" style=" width:442px; height:172px; overflow: hidden;">
                <div id="ipv4" style="height: 145px;display: none">
                    <table width="100%" border="0" cellpadding="0" cellspacing="0" class="date_add_table">
                        <tr>
                            <td align="right"><?=Yii::t('lang','连接类型');?>：</td>
                            <td><label>
                                    <input name="iIPV4ConnectionType" id="iIPV4ConnectionType" type="radio" value="1" onclick="ip4type()" />
                                    <?=Yii::t('lang','静态');?> </label>
                                <label>
                                    <input name="iIPV4ConnectionType" id="iIPV4ConnectionType" type="radio" value="2" onclick="ip4type()" />
                                    dhcp </label></td>
                        </tr>
                        <tr>
                            <td align="right"><?=Yii::t('lang','IP地址');?>：</td>
                            <td><textarea rows="3" style="height: auto;width:200px" class="text"  name="sIPV4Address" id="sIPV4Address" ></textarea></td>
                        </tr>
                    </table>
                    <p><?=Yii::t('lang','IP格式：192.168.2.3/255.255.255.0或192.168.2.3/24。多个IP请分行填写');?></font></p>
                </div>
                <div style="height: 10px;"></div>
                <div id="ipv6" style="height: 155px;display: none">
                    <table width="100%" border="0" cellpadding="0" cellspacing="0" class="date_add_table">
                        <tr>
                            <td align="right"><?=Yii::t('lang','连接类型');?>：</td>
                            <td><label>
                                    <input name="iIPV6ConnectionType" id="iIPV6ConnectionType" type="radio" value="1" onclick="ip6type()" />
                                    <?=Yii::t('lang','静态');?> </label>
                                <label>
                                    <input name="iIPV6ConnectionType" id="iIPV6ConnectionType" type="radio" value="2" onclick="ip6type()" />
                                    dhcp </label></td>
                        </tr>
                        <tr>
                            <td align="right"><?=Yii::t('lang','IP地址');?>：</td>
                            <td><textarea class="text" rows="3"  style="height: auto;width:280px" name="sIPV6Address" id="sIPV6Address" ></textarea>&nbsp;&nbsp;<br/><font color="gray"><?=Yii::t('lang','多个IP请分行填写');?></font></td>
                        </tr>
                        <!--<tr>
                            <td align="right">下一跳：</td>
                            <td><input class="text" name="sIPV6NextJump" /></td>
                        </tr>-->
                    </table>
                </div>
            </div>
        </div>
        <script language="javascript">
            function allsel(n1,n2)
            {
                while(n1.selectedIndex!=-1)
                {
                    var indx=n1.selectedIndex;
                    var t=n1.options[indx].text;
                    n2.options.add(new Option(t));
                    n1.remove(indx);
                }
            }
        </script>

    </form>

</div>


</body>
</html>