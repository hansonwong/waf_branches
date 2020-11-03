<?php
use app\widget\AdminListConfig;
use \yii\helpers\Url;

$tableHeader = AdminListConfig::getTableHeader($table['model'], $table['cols'], $table['operation']);
//$tableData = AdminListConfig::getTableBody($table['data'], $table['cols'], $table['operation']);
?>
<div class="btn_box">
    <div class="btn_list">
    <?php
    foreach ($table['publicButton'] as $k => $v) echo "{$v}&nbsp;";
    ?>
    </div>
    <div class="aearch_box">
        <form action="" method="post">
            <input type="button" id="queryAccurate" class="btn btn_sea" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('queryAccurate')?>" >
        </form>
    </div>
</div>
<?=$searchForm?>
<script>
    //删除数据
    function dataDelete(obj, id, query) {
        var primaryKey = [];
        var msg = top.translation.t('deleteConfirm');
        if ('' == id) {
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
        } else {
            primaryKey.push(id);
        }
        document.querySelectorAll('.l-grid-hd-row')[1].className = 'l-grid-hd-row';

        $.Layer.confirm({
            title: top.translation.t('systemFriendlyTips'), msg:'<span class=red>' + msg + '</span>', fn: function () {
                $.ajax({
                    url: '<?=Url::to(['delete'])?>&' + query,
                    type: 'POST',
                    data: {
                        id: primaryKey,
                        _csrf: $('meta[name=csrf-token]').attr('content'),
                    },
                    dataType: 'json',
                    timeout: 5000,
                    cache: false,
                    async: false,
                    success: function (data) {
                        switch(data.success){
                            case true:
                                $.grid.reload();
                                break;
                            case false:
                                $.Layer.alert({msg: data.msg,});
                                break;
                        }

                    },
                });
            }
        });
    }

    //使用url打开弹框
    function dataBox(title, url, w, h) {
        var dialog = $.Layer.iframe(
            {
                title: title,
                url:url,
                width: getWindowSize(w),
                height: getWindowSize(h)

            });
        var table = $.grid;
        dialog.hGrid = table;
    }

    //编辑数据
    function dataEdit(title, id, w, h) {
        var url = ('' == id) ? '<?=Url::to(['create'])?>' : '<?=Url::to(['update'])?>&id=' + id;

        var dialog = $.Layer.iframe(
            {
                title: title,
                url:url,
                width: getWindowSize(w),
                height: getWindowSize(h)
            });
        var table = $.grid;
        dialog.hGrid = table;
    }

    //查看数据
    function dataView(title, id, w, h) {
        var url = '<?=Url::to(['view'])?>&id=' + id;

        $.Layer.iframe(
            {
                title: title,
                url:url,
                width: getWindowSize(w),
                height: getWindowSize(h)

            });
    }

    //清空数据
    function dataEmpty(){
        $.Layer.confirm({
            title: top.translation.t('systemFriendlyTips'), msg:'<span class=red>' + top.translation.t('emptyWillNotBeRestored') + '</span>', fn: function () {
                $.ajax({
                    url: '<?=Url::to(['empty-data'])?>',
                    type: 'POST',
                    data: {
                        _csrf: $('meta[name=csrf-token]').attr('content'),
                    },
                    dataType: 'json',
                    timeout: 5000,
                    cache: false,
                    async: false,
                    success: function (data) {
                        switch(data.success){
                            case true:
                                $.grid.reload();
                                break;
                            case false:
                                $.Layer.alert({msg: data.msg,});
                                break;
                        }

                    },
                });
            }
        });
    }

    //获取窗口宽高
    function getWindowSize(size) {
        var checkNum = function(s) {
            var patrn=/^\d*$/;
            if (patrn.test(s)) {
                return true;
            } else {
                return false;
            }
            return false;
        }
        if(checkNum(size)) return parseFloat(size);

        var wh = 0;
        switch (size) {
            case 'maxW' :
                wh = window.innerWidth * 0.97;
                break;
            case 'maxH' :
                wh = window.innerHeight * 0.97;
                break;
            default :
                if(-1 != size.indexOf('WP')) wh = window.innerWidth * parseFloat(size.replace('WP',''));
                if(-1 != size.indexOf('HP')) wh = window.innerHeight * parseFloat(size.replace('HP',''));
        }
        return wh;
    }
</script>
<script>
    var tableHeader = <?=json_encode($tableHeader)?>;
    //var tableData = <?=json_encode($tableData ?? [])?>;
    var hListTabel = null;
    var hListTabelConfig = {//调用ligerUI的列表插件
        checkbox: true,
        el: '#maingrid',
        checkbox: true,
        columns: tableHeader,
        rownumbers: false,
        root: 'data',//数据
        pageParmName:'page',//页码
        pagesizeParmName:'pagesize',//页数据量
        record: 'total',//总数
        width: '99.8%',
        height: '99%',
        pageSize:20,
        pageSizeOptions: [20, 30, 40, 50, 60],
    };

    $(function(){
        hListTabelConfig.ajax = {
            url: '<?=Url::toRoute(['', 'header' => 1])?>',
                type: 'POST',
                parms:$("#search_form").serializeArray(),
        };
    });
</script>
<div id="maingrid" class="list"></div>
<?=$table['customStr']?>
<script>
$(function(){
    hListTabel = $.CreateTabel(hListTabelConfig);
});
</script>
