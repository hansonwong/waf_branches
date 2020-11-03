<?php
use \yii\helpers\Url;
?>
<script>
    //hListTabelConfig.usePager = false;//不分页
    /*hListTabelConfig.detail = {
        height: 'auto', onShowDetail: function (r, p) {
            var id = r.primaryKey;
            $.ajax({
                url: '<?php echo Url::to(['index', 'op' => 'detail']);?>',
                type: 'POST',
                dataType: "json",
                data: {'_csrf': $('[name=_csrf]').val(), 'id': id},
                cache: false,
                timeout: 30000,
                success: function(data){
                    var service = '';
                    for(var key in data.service){
                        service += `<span style="margin-right: 15px;">${key}:${data.service[key]}</span>&nbsp;`;
                    }
                    var os = '';
                    for(var key in data.os){
                        os += `<span style="margin-right: 15px;">${key}</span>&nbsp;&nbsp;`;
                    }

                    var el = `<table cellpadding="0" cellspacing="0" style="width:95%;" class="detailtd">
                        <tr>
                            <td align="right" class="dtd" width="120">service and port</td>
                            <td>${service}</td>
                        </tr>
                        <tr>
                            <td align="right" class="dtd" width="120">Os</td>
                            <td>${os}</td>
                        </tr>
                        </table>`;
                    $(p).append($(el).css('margin', '20px auto'));
                }
            });
        }
    };*/

    function scanStatusShow(){
        $.ajax({
            url: '<?=Url::to(['config', 'op' => 'show'])?>',
            type: 'POST',
            data: $("#search_form").serialize(),
            dataType: 'json',
            timeout: 5000,
            cache: false,
            async: false,
            success: function (data) {
                switch(data.success){
                    case true:
                        var info = data.data;
                        var msg = 'IP:' + info.ip + '&nbsp;&nbsp;' +
                            top.translation.t('enable') + ' : ' +
                            ((1 == info.enable) ? 'Yes':'No')
                            + '&nbsp;&nbsp;' +
                            top.translation.t('status') + ' : ' +
                            ((0 == info.status) ? 'Loading...':'Finish...')
                            + '&nbsp;&nbsp;';
                        $('#scanStatus').html(msg);
                        break;
                    case false:
                        $.Layer.alert({msg: data.msg,});
                        break;
                }

            },
        });
    }
    $(function(){
        //setInterval(searchByLigerUi, 15000);//轮询扫描结果
        setInterval(scanStatusShow, 6000);//轮询扫描结果
    });
</script>
