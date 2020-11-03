<!DOCTYPE HTML>
<html><head>
	<meta charset="UTF-8">
    <title><?php echo Yii::app()->name ?></title>
    <?php $this->renderPartial('/layouts/js_css'); ?>
    <?php $this->renderPartial('/layouts/ext_table'); ?>
    <?php $this->renderPartial('/layouts/ext_datetime'); ?>
    <?php $this->renderPartial('/layouts/ext_validation'); ?>
    <script type="text/javascript">var save_path=$.PhpUrl("Systemsetting/PacketCaptureSave");</script>
<!--    <script type="text/javascript" src="<?php /*echo Yii::app()->getTheme()->getBaseUrl()*/?>/js/jquery-1.11.3.min.js"></script>-->
    <script type="text/javascript" src="<?php echo Yii::app()->getTheme()->getBaseUrl()?>/js/act/packet_capture_save.js"></script>

    <style type="text/css">
        .openWin input[type="text"]{width:170px;}
        .date_add_table {width: 750px;}
        .date_add_table tbody{ border:1px solid #C4D0DC;border-left:0; border-spacing:0px; border-collapse: collapse;}
        .date_add_table tbody th{ background:#F0F7FD; border:1px solid #C4D0DC;  border-top:1px dashed #d7d7d7;border-bottom:1px dashed #d7d7d7; padding-right:10px;text-align: right}
        .date_add_table tbody td{vertical-align:center; padding-left:10px; border-top:1px dashed #d7d7d7;}
    </style>
</head>
<body>
<div class="openWin" style="padding:0px 10px;">

    <form action="" method="post" id="form_id" class="edit_form" >
        <input type="hidden" id="id" name="id" value=""/>
        <table width="100%" border="0" cellpadding="0" cellspacing="0" class="date_add_table" style="border-left:1px solid #C4D0DC;border-right:1px solid #C4D0DC;">
            <tbody>
            <tr>
                <td class="t_r" width="15%"><span class="red">*</span> <?=Yii::t('lang','名称');?></td>
                <td><input name="sName" class="validate[required,custom[name_rule]] text" /></td>
                <td class="t_r" ><input type="button" value="<?=Yii::t('lang','启用抓包');?>" class="btn_ty "></td>
                <td><label><input type="checkbox" name="iStatus" value="1"/></label></td>
            </tr>
            <tr>
                <td class="t_r" width="15%"><span class="red">*</span> <?=Yii::t('lang','运行时间');?></td>
                <td><input name="iRunTime"  class="validate[required,min[1],max[65535],custom[integer2]] text" style="width:60px;"/> <?=Yii::t('lang','秒');?></td>
                <td class="t_r" ><input type="button" value="<?=Yii::t('lang','新建抓包');?>" class="btn_ty btn_new"></td>
                <td><?=Yii::t('lang','最多可新建32个抓包接口');?></td>
            </tr>
            </tbody>
        </table>
         <table id="pack" width="100%" border="0" cellpadding="0" cellspacing="0" class="date_add_table" >
            <tbody class="item">
                <tr>
                    <th class="t_r"><span class="red">*</span> <?=Yii::t('lang','网络接口');?> <span class="org">1</span></th>
                    <td>
                        <select type="text" name="sPortName[]" class="validate[required] text">
                                <option value=""><?=Yii::t('lang','请选择');?></option>
                            <?php foreach($netPortList as $item){?>
                                <option value="<?=$item['sPortName']?>"><?=$item['sLan']?></option>
                            <?php } ?>
                        </select>
                    </td>
                    <th><input type="button" value="<?=Yii::t('lang','删除');?>" class="btn c_o" onclick="btn_del(this)" style="padding:3px 12px"><input type="hidden" name="pack_id[]" /><input type="hidden" name="sLan[]" /> </th>
                    <td></td>
                </tr>
                <tr>
                    <th class="t_r"><span class="red">*</span> <?=Yii::t('lang','CAP文件名称');?></th>
                    <td> <input type="text" name="sNameCap[]" class="validate[required,custom[name_rule]] text"/></td>
                    <th class="t_r"><?=Yii::t('lang','CAP文件容量');?></th>
                    <td> <input type="text" name="iCapacityCap[]" class="text validate[custom[integer2],min[1],max[30]]"/> M</td>     
                </tr>

                <tr>
                    <th class="t_r"><?=Yii::t('lang','源IP或端口');?></th>
                    <td> <input type="text" name="sAddress1[]" class="validate[custom[ipv4]] text"/>/
                          <input type="text" name="iNetmask1[]" class="validate[min[1],max[65535],custom[integer2]] text" style="width:60px;"/></td>
                    <th class="t_r"><?=Yii::t('lang','协议');?></th>
                    <td> <select name="sProtocol[]" class="text validate[condRequired[sSourcePort,sTargetPort]]" >
                            <option value=""><?=Yii::t('lang','请选择');?></option>
                            <option value="TCP">TCP</option>
                            <option value="UDP">UDP</option>
                            <option value="ICMP">ICMP</option>
                        </select>
                    </td>  
                </tr>
                <tr>
                    <th class="t_r"><?=Yii::t('lang','目的IP或端口');?></th>
                    <td> <input type="text" name="sAddress2[]" class="validate[custom[ipv4]] text"/>/
                          <input type="text" name="iNetmask2[]" class="validate[min[1],max[65535],custom[integer2]] text" style="width:60px;"/></td>
                    <th class="t_r"><?=Yii::t('lang','捕获包长度');?></th>
                    <td> <input type="text" name="iPacketCapNum[]" class="validate[min[1],custom[integer2]] text"/></td>     
                </tr>
                <tr>
                    <th class="t_r"><?=Yii::t('lang','任意方向IP或端口');?></th>
                    <td> <input type="text" name="sAddress3[]" class="validate[custom[ipv4]] text"/>/
                          <input type="text" name="iNetmask3[]" class="validate[min[1],max[65535],custom[integer2]] text" style="width:60px;"/></td>
                    <th class="t_r"><?=Yii::t('lang','抓包数');?></th>
                    <td> <input type="text" name="iPacketNum[]" class="validate[min[1],custom[integer2]] text"/></td>
                </tr>
            </tbody>

         </table>
        <br />
    </form>
</div>


<!--抓包-->
<div >
<table id="pack_item"   style="display:none;">
    <tbody class="item">
        <tr>
            <th class="t_r"><span class="red">*</span> <?=Yii::t('lang','网络接口');?> <span class="org">1</span></th>
            <td>
                <select type="text" name="sPortName[]" class="validate[required] text">
                    <option value=""><?=Yii::t('lang','请选择');?></option>
                    <?php foreach($netPortList as $item){?>
                        <option value="<?=$item['sPortName']?>"><?=$item['sLan']?></option>
                    <?php } ?>
                </select>
            </td>
            <th><input type="button" value="<?=Yii::t('lang','删除');?>" class="btn c_o" onclick="btn_del(this)" style="padding:3px 12px"><input type="hidden" name="pack_id[]" /><input type="hidden" name="sLan[]" /> </th>
            <td></td>
        </tr>
        <tr>
            <th class="t_r"><span class="red">*</span> <?=Yii::t('lang','CAP文件名称');?></th>
            <td> <input type="text" name="sNameCap[]" class="validate[required,custom[name_rule]] text"/></td>
            <th class="t_r"><?=Yii::t('lang','CAP文件容量');?></th>
            <td> <input type="text" name="iCapacityCap[]" class="text validate[custom[integer2],min[1],max[30]]"/> M</td>     
        </tr>

        <tr>
            <th class="t_r"><?=Yii::t('lang','源IP或端口');?></th>
            <td> <input type="text" name="sAddress1[]" class="validate[custom[ipv4]] text"/>/
                  <input type="text" name="iNetmask1[]" class="validate[min[1],max[65535],custom[integer2]] text" style="width:60px;"/></td>
            <th class="t_r"><?=Yii::t('lang','协议');?></th>
            <td> <select name="sProtocol[]" class="text validate[condRequired[sSourcePort,sTargetPort]]" >
                    <option value=""><?=Yii::t('lang','请选择');?></option>
                    <option value="TCP">TCP</option>
                    <option value="UDP">UDP</option>
                    <option value="ICMP">ICMP</option>
                </select>
            </td>  
        </tr>
        <tr>
            <th class="t_r"><?=Yii::t('lang','目的IP或端口');?></th>
            <td> <input type="text" name="sAddress2[]" class="validate[custom[ipv4]] text"/>/
                  <input type="text" name="iNetmask2[]" class="validate[min[1],max[65535],custom[integer2]] text" style="width:60px;"/></td>
            <th class="t_r"><?=Yii::t('lang','捕获包长度');?></th>
            <td> <input type="text" name="iPacketCapNum[]" class="validate[min[1],custom[integer2]] text"/></td>     
        </tr>
        <tr>
            <th class="t_r"><?=Yii::t('lang','任意方向IP或端口');?></th>
            <td> <input type="text" name="sAddress3[]" class="validate[custom[ipv4]] text"/>/
                  <input type="text" name="iNetmask3[]" class="validate[min[1],max[65535],custom[integer2]] text" style="width:60px;"/></td>
            <th class="t_r"><?=Yii::t('lang','抓包数');?></th>
            <td> <input type="text" name="iPacketNum[]" class="validate[min[1],custom[integer2]] text"/></td>
        </tr>
    </tbody>
    </table>
</div>
</body>
</html>