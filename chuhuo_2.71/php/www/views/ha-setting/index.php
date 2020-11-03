<?php
$translate = Yii::$app->sysLanguage;
use yii\helpers\Html;
use \yii\helpers\Url;
?>
<div class="openWin">
<form action="" method="post" id="form_id">
    <input id="id" name="id" type="hidden" value="<?= Html::encode($hasetting->id) ?>"/>
  <h1><?=$translate->getTranslateBySymbol('HaConfigAttrs')?></h1>
  <div class="jbxx sj">
    <table width="80%" border="0" cellspacing="0" cellpadding="0" class="date_add_table">
      <tr>
        <td width="180" class="t_r"><?=$translate->getTranslateBySymbol('HaConfigVipSwitch')?>：</td>
        <td ><label><input name="is_use" type="checkbox" value="1" <?php if ($hasetting['is_use'] == 1) {echo 'checked="checked"';} ?> /> <?=$translate->getTranslateBySymbol('isEnable')?>.(<?=$translate->getTranslateBySymbol('status')?>：<?=$hasetting['state']?>)
      </tr>
      <tr>
        <td class="t_r">VIP：</td>
        <td >
          <input name="vip" type="text" value="<?=$hasetting['ip']?>" class="validate[custom[ipv4]，maxSize[15]] text"/>
        </td>
      </tr>
      <tr>
        <td class="t_r"> <?=$translate->getTranslateBySymbol('monitoringConnector')?>：</td>
        <td >
          <select id="interface" class="text">
              <?php foreach ($nics as $value) {
                  $selected = $hasetting['interface'] == $value['sPortName'] ? "selected" : '';
                  echo "<option value='{$value['sPortName']}' {$selected}>{$value['sPortName']}</option>";
              }?>
          </select>
        </td>
      </tr>      
      <tr>
        <td class="t_r"> <?=$translate->getTranslateBySymbol('priority')?>：</td>
        <td >
          <input name="priority" type="text" class="validate[custom[integer],min[0],max[255]] text" value="<?=$hasetting['priority']?>" />
          <span>（* <?=$translate->getTranslateBySymbol('Limit0~255')?>）</span>
        </td>
      </tr> 
      <tr>
        <td width="180" class="t_r"> <?=$translate->getTranslateBySymbol('connectorAggregation')?>：</td>
        <td ><label><input name="is_port_aggregation" type="checkbox" <?php if ($hasetting['is_port_aggregation'] == 1) {echo 'checked="checked"'; } ?> /> <?=$translate->getTranslateBySymbol('isEnable')?></label></td>
      </tr> 
      <tr>
        <td class="t_r"> <?=$translate->getTranslateBySymbol('bridgeConnector')?>：</td>
        <td >
          <select id="bridge" class="text">
              <?php foreach ($bridge as $value) {
                  $selected = $hasetting['bridge'] == $value['sPortName'] ? "selected" : '';
                  echo "<option value='{$value['sPortName']}' {$selected}>{$value['sPortName']}</option>";
              }?>
          </select>
        </td>
      </tr>
      <tr>
        <td width="180" class="t_r"> <?=$translate->getTranslateBySymbol('databaseConfigSync')?>：</td>
        <td ><label><input name="database_sync_status" type="checkbox" <?php if ($hasetting['database_sync_status'] == 1) {echo 'checked="checked"';} ?>/> <?=$translate->getTranslateBySymbol('isEnable')?></label></td>
      </tr>
      <tr>
        <td class="t_r"> <?=$translate->getTranslateBySymbol('portVsPort')?>waf IP：</td>
        <td >
          <input name="database_ip" type="text" value="<?= $hasetting['database_ip']?>" class="validate[custom[ipv4]，maxSize[15]] text"/>
        </td>
      </tr>
      <tr>
        <td>&nbsp;</td>
        <td>
          <input  type="button" onclick="return doSubmit();" id="btnOk" class="btn_ty" value=" <?=$translate->getTranslateBySymbol('done')?>" />
        </td>
      </tr>                                         
    </table>
  </div>  
</form>
</div>

<script type="text/javascript">

    ;(function ($) {
        $(function (){
            $("#form_id").validationEngine({
                promptPosition:'centerRight: 0, -4',scroll: false , binded: true ,'custom_error_messages': {
                    // Custom Error Messages for Validation Types
                    'required': {
                        'message': '* 该项必须填写！'
                    },
                    'custom': {
                        'message': '* 请输入正整数！'
                    },
                    'min': {
                        'message': '* 请输入大于0的正整数！'
                    },
                    'max': {
                        'message': '* 请输入小于255的正整数！'
                    }
                }
            });
        });
    })(jQuery);

    function doSubmit()
    {
        var id = $('#id').val();
        var is_use  =  $('input[name="is_use"]').is(':checked') ? 1 : 0;
        var interface  = $('#interface option:selected').val();
        var bridge  = $('#bridge option:selected').val();
        var ip = $('input[name="vip"]').val();
        //var vhid = $('#vhid').val();
        var database_ip = $('input[name="database_ip"]').val();
        var database_sync_status  =  $('input[name="database_sync_status"]').is(':checked') ? 1 : 0;
        var priority = $('input[name="priority"').val();
        //var database_port = $('#database_port').val();
        //var password = $('#password').val();
        //var state = $('#state').val();
        var is_port_aggregation  =  $('input[name="is_port_aggregation"]').is(':checked') ? 1 : 0;


        var _csrf = $('meta[name=csrf-token]').attr('content');

        //if(state == '') state = "backup";
        $.ajax({
            url: '<?php echo Url::to(['update']);?>'+'&id='+id,
            type: 'POST',
            dataType: "json",
            data:{'_csrf':_csrf, 'HaSetting[is_use]':is_use, 'HaSetting[interface]':interface, 'HaSetting[bridge]':bridge, 'HaSetting[ip]':ip, 'HaSetting[database_ip]':database_ip, 'HaSetting[database_sync_status]':database_sync_status, 'HaSetting[priority]':priority, 'HaSetting[is_port_aggregation]':is_port_aggregation},
            cache: false,
            timeout: 30000,
            success: function(data){
                $.Layer.alert({msg:data['info']});
            }
        });
    }


</script>

