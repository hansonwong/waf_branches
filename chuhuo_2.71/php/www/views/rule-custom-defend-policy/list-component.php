<?php
use \yii\helpers\Url;
$url = Url::to([$config['url'] ?? 'update-status']);
$jsFuntionName = $config['jsFuntionName'] ?? 'statusChange';
?>
<script>
    function <?=$jsFuntionName?>(id, status){
        var primaryKey = [];
        if (0 < id) {
            primaryKey.push(id);
        } else {
            var list = $.grid.getSelectedRows();
            var i = 0;
            for(var item in list){
                i++;
                var obj =list[item];
                primaryKey.push(obj['primaryKey']);
            }
            if(0 == i){
                $.Layer.alert({msg: top.translation.t('noDataSelection'),});
                return;
            }
        }
        document.querySelectorAll('.l-grid-hd-row')[1].className = 'l-grid-hd-row';

        $.ajax({
            url: '<?=$url?>',
            type: 'POST',
            data: {
                id: primaryKey,
                status: status,
                _csrf: $('meta[name=csrf-token]').attr('content'),
            },
            dataType: 'json',
            timeout: 5000,
            cache: false,
            async: false,
            success: function (data) {
                $.grid.reload();
            },
        });
    }
</script>
