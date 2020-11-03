<!DOCTYPE HTML>
<html><head>
	<meta charset="UTF-8">
    <title><?php echo Yii::app()->name ?></title>
    <?php $this->renderPartial('/layouts/js_css'); ?>
    <?php $this->renderPartial('/layouts/ext_table'); ?>
    <?php $this->renderPartial('/layouts/ext_datetime'); ?>
    <?php $this->renderPartial('/layouts/ext_validation'); ?>
    <script type="text/javascript">var save_path=$.PhpUrl('Network/BridgeDeviceSave')</script>
	<script type="text/javascript" src="<?php echo Yii::app()->getTheme()->getBaseUrl()?>/js/act/common_save.js"></script>
    <script type="text/javascript">
        $(document).ready(function() {
            //新增任务菜单切换
            $(".addlist-tab ul li").click(function(){
                $(".addlist-tab ul li").removeClass();
                $(this).addClass("addsel");
            });

			var id=$("#id").val();

            var dialog = top.getDialog();
            var data = dialog.hData;

            if(id!='') {
				var devices=data.sBindDevices.split(",");
				var devicesLan=data.sBindDevicesLan.split(",");
				for(var i in devices){
					$("#sel_place2").append('<option value="'+devices[i]+'">'+devicesLan[i]+'</option>');
				}
                $("#sBridgeName").val(data['sBridgeName'].replace("bridge",""));
            }

            if(data){
                var fields = $("form.edit_form").serializeArray();
                jQuery.each(fields, function (i, field) { //jquery根据name属性查 找
                    if(field.name =='sIPV4'){
                        var str = data['sIPV4'];
                        var nStr= '';
                        strs=str.split(","); //字符分割
                        for (i=0;i<strs.length ;i++ )
                        {
                            nStr+=strs[i]+"\r\n"; //分割后的字符输出
                        }
                        $(":input[name='" + field.name + "']").val(nStr);
                    }
                    if(field.name =='sIPV6'){
                        var str = data['sIPV6'];
                        var nStr= '';
                        strs=str.split(","); //字符分割
                        for (i=0;i<strs.length ;i++ )
                        {
                            nStr+=strs[i]+"\r\n"; //分割后的字符输出
                        }
                        $(":input[name='" + field.name + "']").val(nStr);
                    }
                });
            }
            
        });
    </script>
</head>
<body>
<div class="openWin">
    <form name="form1" method="post" action="" class="edit_form">
        <input type="hidden" name="id">
        <input type="hidden" name="iStatus">
        <table cellpadding="0" cellspacing="0" height="200" class="selbox">
            <tr>
                <td colspan="3" valign="top" style="padding-top:28px;padding-left:32px;"><?=Yii::t('lang','桥接口名称');?> ：
                    bridge <input type="text" name="sBridgeName" id="sBridgeName" style="width:100px;" class="validate[required,custom[integer],min[0],max[255]] text">
				</td>
            </tr>
            <tr>
                <td width="150" valign="top"><table width="150" class="seltab">
                        <tr>
                            <th align="center"><?=Yii::t('lang','可选绑定设备列表');?> </th>
                        </tr>
                        <tr>
                            <td align="center" bgcolor="#FFFFFF"><select name="sel_place1" size="10" multiple="multiple" id="sel_place1" style="width:150px; height:150px; " >
                                    <?php foreach($netPortList as $port){?>
                                        <option value="<?=$port['sPortName']?>"><?=$port['sLan']?></option>
                                    <?php }

                                    ?>
                                </select>
							</td>
                        </tr>
                    </table></td>
                <td align="center" valign="center" height="200">
					<input class="selbutright" name="sure2" type="button" id="sure2" onclick="allsel(this, document.form1.sel_place1,document.form1.sel_place2);" />
                    <input class="selbutleft" name="sure1" type="button" id="sure1" onclick="allsel(this, document.form1.sel_place2,document.form1.sel_place1);" />
                </td>
                <td width="150" valign="top"><table width="150" border="0" class="seltab">
                        <tr>
                            <th align="center"><?=Yii::t('lang','绑定设备列表');?> </th>
                        </tr>
                        <tr>
                            <td align="center" bgcolor="#FFFFFF">
                                <input type="hidden" name="sBindDevices" id="sBindDevices">
                                <select name="sel_place2" size="10" multiple="multiple" id="sel_place2" style="width:150px; height:150px;">
                                </select>
                            </td>
                        </tr>
                    </table></td>
            </tr>
        </table>
        <p style="padding-left: 15px;height: 25px;"><?=Yii::t('lang','设备列表可以按Ctrl或者Shift键进行多选左右移动');?></p>
        <div class="addlist-data">
            <div class="addlist-tab mar_top">
                <ul>
                    <li class="addsel"><a href="#ipv4">IPV4</a></li>
                    <li><a href="#ipv6">IPV6</a></li>
                </ul>
            </div>

            <div class="sl-content" style=" width:392px; height:170px; overflow: hidden;">
                <div id="ipv4">
                    <table width="100%" border="0" cellpadding="0" cellspacing="0" class="date_add_table">
                        <tr>
                            <td align="right"><?=Yii::t('lang','IP地址');?>：</td>
                            <td>
                                <textarea rows="3" style="height: auto;width:200px" class="text"  name="sIPV4" id="sIPV4" ></textarea>
                                <br><font color="gray" ><?=Yii::t('lang','格式：192.168.2.3/255.255.255.0');?><br><?=Yii::t('lang','或192.168.2.3/24');?><br><?=Yii::t('lang','多个IP请分行填写');?></font>
                            </td>
                        </tr>
                    </table>
                </div>
                <div style="height: 20px;"></div>
                <div id="ipv6" style="height: 155px;">
                    <table width="100%" border="0" cellpadding="0" cellspacing="0" class="date_add_table">
                        <tr>
                            <td align="right"><?=Yii::t('lang','IP地址');?>：</td>
                            <td>
                                <textarea class="text" rows="3"  style="height: auto;width:280px" name="sIPV6" id="sIPV6" ></textarea>&nbsp;&nbsp;
                                <br/><font color="gray"><?=Yii::t('lang','格式: FE80::1/64 多个IP请分行填写');?></font>
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
                            <td align="left" ><label style=" padding-left:6px;">
                                <input name="iWeb" id="iWeb" type="checkbox" value="1" onclick="logopen()" /> WEBUI
                            </label> </td>
                            <td align="left" ><label>
                                <input name="iSSH" id="iSSH" type="checkbox" value="1" onclick="logopen()" /> SSH
                            </label> </td>
                            <td align="left"><label>
                                    <input name="iAllowPing" id="iAllowPing" type="checkbox" value="1" />&nbsp;<?=Yii::t('lang','允许PING');?>
                                </label></td>
                            <td align="left"><label>
                                    <input name="iAllowTraceRoute" id="iAllowTraceRoute" type="checkbox" value="1" />&nbsp;<?=Yii::t('lang','允许Traceroute');?>
                                </label> </td>
                            <td align="left"><label id="iAllowLog_label">
                                    <input name="iAllowLog" id="iAllowLog" type="checkbox" value="1" /> <?=Yii::t('lang','日志');?>
                                </label> </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        <script language="javascript">
            function allsel(th,n1,n2)
            {
                // 获取 可选绑定设备列表 被选中数据
                var n1Value = [];
                $(n1).find("option:selected").each(function(){
                    n1Value.push($(this).val());
                });

                //可选绑定设备列表 选择超过2个后，提示 不支持选择超过两个设备
                if( n1Value.length>2 && th.name==='sure2' )
                {
                    art.dialog({icon: 'warning', content:top.translation.t('chooseNotToSelectMoreThanTwoDevices'), time: 2});
                    return;
                }

                //可选绑定设备列表 选中个数与绑定设备列表数量大于2，提示 不支持选择超过两个设备
                if( $(n2).find("option").length + n1Value.length>2 && th.name==='sure2' )
                {
                    art.dialog({icon: 'warning', content:top.translation.t('chooseNotToSelectMoreThanTwoDevices'), time: 2});
                    return;
                }

                var aPortName = []; // 保存提交检测是否内外网口的数据
                var sBindDevicesValue = $("#sBindDevices").val();
                if( sBindDevicesValue.length>0 )  aPortName.push(sBindDevicesValue);
                for (var i = 0; i < n1Value.length; i++)
                {
                    aPortName.push(n1Value[i]);

                    // 判断两个网口，是不是一个外网一个内网
                    if( aPortName.length===2 && th.name==='sure2' )
                    {
                        var sPortName = JSON.stringify(aPortName);
                        var rst = [];
                        $.ajax({
                            type:'GET',
                            url:'/waf.php?r=api-common/get-net-ports',
                            dataType:'json',
                            data:{sPortName: sPortName},
                            async:false,
                            success:function(data){
                                rst = data;
                            }
                        });

                        if( rst.code!=='T' )
                        {
                            art.dialog({icon: 'warning', content: rst.info, time: 2});

                            return;
                        }

                        var counter = 0;
                        rst.data.map(function (v) {
                            counter += parseInt(v);
                        });
                        if( counter !== 3 )
                        {
                            //绑定桥必须是一个外网口与一个内网口
                            art.dialog({icon: 'warning', content:top.translation.t('theBoundBridgeMustBeAnOuterWebPortAndAnIntranet'), time: 3});
                            return;
                        }
                    }
                }

                while( n1.selectedIndex!==-1 )
                {
                    var index = n1.selectedIndex;
                    var tValue = n1.options[index].value;
                    var tText = n1.options[index].text;

                    n2.options.add(new Option(tText ,tValue));
                    n1.remove(index);
                }

				//赋值给隐藏域
				var devices='';
				$("#sel_place2 option").each(function(i,opt){
                    devices += opt.value+',';
				});

				if( devices.length>0 )
				{
                    devices = devices.substr(0,devices.length-1);
				}
				$("#sBindDevices").val(devices);
            }
        </script>

    </form>

</div>

</body>
</html>