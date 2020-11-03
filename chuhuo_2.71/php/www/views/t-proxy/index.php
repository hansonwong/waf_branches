<?php
use \yii\helpers\Url;
use yii\helpers\Html;
?>
<div class="list_page">
    <div class="btn_box">
        <div class="btn_list">
            <!--添加-->
            <input name="b_add" id="b_add" type="button" class="btn c_g btn_add" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('add') ?>">
            <!--删除-->
            <input name="b_del" id="b_del" type="button" class="btn c_o btn_del" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('delete') ?>">
            <!--刷新-->
            <input name="b_ref" id="b_ref" type="button" class="btn c_b btn_ref" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('refresh') ?>">
        </div>
    </div>
    <div id="maingrid"  class="list"></div>
</div>
<script language="javascript">
    (function ($) {  //避免全局依赖,避免第三方破坏
        $(document).ready(function () {
            var _csrf = $('meta[name=csrf-token]').attr('content');

            // 是否启用函数
            var fnStatus = function (row, index, value) {
                if ( parseInt(value) === 1 ) {
                    //启用
                    return "<input type='button' rowid='"+index+"' class='qt bt_qyan' title='<?=Yii::$app->sysLanguage->getTranslateBySymbol('enable') ?>' />";
                } else{
                    // 停用
                    return "<input type='button' rowid='"+index+"' class='qt bt_tyan' title='<?=Yii::$app->sysLanguage->getTranslateBySymbol('stopUse') ?>'/>";
                }
            };

            /*调用*/
            var GridTable = $.BDGrid({
                _csrf: _csrf,
                sColumnsUrl: "<?php echo Url::to(['index', 'op' => 'header']);?>",
                ajax: {
                    url: "<?php echo Url::to(['index']);?>",
                    type: 'POST',
                    parms: {_csrf:_csrf} // yii2需要传的参数
                },
                el: '#maingrid',
                dataAction: 'server',
                showSitting: false,//是否需要操作列
                showEdit: true,
                showView: false,
                showDel: true,
                showLock: false,//是否需要解锁和锁定状态栏
                isSelectR: true,//复选按钮是否选中
                allowHideColumn: false, //是否显示'切换列层'按钮
                root: 'data',//数据
                pageParmName:'page',//页码
                pagesizeParmName:'pagesize',//页数据量
                record: 'total',//总数
                width: '99.8%',
                height: '98.5%',
                pageSize: 20,
                pageSizeOptions: [10, 20, 30, 40, 50, 100],
                showRuning: false,
                checkbox: true,
                columnDefs: [   // change
                    {
                        data: 'status',
                        targets: 'iStatus',
                        render: fnStatus
                    }
                ]
            });

            GridTable.on('beforerender', function (e, grid) {
                // 是否启用
                $(".g_div_table").delegate("input.qt", "click", function (e) {
                    e.preventDefault();
                    var  data = grid.getRow($(this).attr('rowid'));
                    var status;
                    if($(this).hasClass('bt_qyan')){
                        $(this).addClass('bt_tyan').removeClass('bt_qyan');
                        $(this).attr('title',"<?=Yii::$app->sysLanguage->getTranslateBySymbol('stopUse') ?>"); // 停用
                        status = 0;
                    }else{
                        $(this).addClass('bt_qyan').removeClass('bt_tyan');
                        $(this).attr('title',"<?=Yii::$app->sysLanguage->getTranslateBySymbol('enable') ?>"); //启用
                        status = 1;
                    }

                    var idArr = [];
                    idArr[0] = data.id;
                    // 转换json数据提交
                    idArr = JSON.stringify(idArr);
                    $.ajax({
                        url: '<?php echo Url::to(['update', 'op'=>'status']);?>',
                        type: 'POST',
                        dataType: "json",
                        data:{'_csrf':_csrf, 'status':status, 'idArr':idArr},
                        cache: false,
                        timeout: 30000,
                        success: function(data){
                            if( data.code==='T' )
                            {
                                $.grid.reload();
                                art.dialog({icon: 'succeed', content: data.info, time: 1});
                            }
                            else
                            {
                                art.dialog({icon: 'error', content: data.info, time: 2});
                            }
                        }
                    });
                });
            });

            // 添加
            $('.list_page').on('click', 'input.btn_add', function () {
                var dialog = $.Layer.iframe(
                    {
                        title: "<?=Yii::$app->sysLanguage->getTranslateBySymbol('add') ?>", // 添加
                        url:"<?php echo Url::to(['create']);?>",
                        width: 430,
                        height: 550
                    });
                dialog.hGrid = $.grid;
            });

            //编辑
            GridTable.on('edit', function (e, c, table, data) {
                e.preventDefault();
                if (data.length === 1) {
                    var dialog = $.Layer.iframe({
                        title: "<?=Yii::$app->sysLanguage->getTranslateBySymbol('modify') ?>", // 修改
                        url: "<?php echo Url::to(['update']);?>&id="+data[0]['id'],
                        width: 430,
                        height: 550
                    });
                    dialog.hData = data[0];
                    dialog.hGrid = table;
                } else {
                    $.Layer.confirm({
                        msg: "<?=Yii::$app->sysLanguage->getTranslateBySymbol('selectOneRowData') ?>", fn: function () { } //请选择某一行数据
                    });
                }
            });

            // 刷新
            $('.list_page').on('click', 'input.btn_ref', function(e) {
                e.preventDefault();
                $.grid.reload();
            });

            //删除数据
            $('.list_page').on('click', 'input.btn_del,a.bt_del', function(e) {
                e.preventDefault();
                var $this = $(this);
                var rows = $.grid.getSelectedRows();//批量删，获取对象组
                var row = $.grid.getRow($this.attr('rowid'));//单删，获取对象

                // 判断是不是按了多行选择删除方式
                if( !rows.length>0 && $this[0].tagName == 'INPUT' )
                {
                    $.Layer.confirm({msg : "<?=Yii::$app->sysLanguage->getTranslateBySymbol('selectDeleteData') ?>", fn : function() { //请选择要删除的数据
                    }});
                    return;
                }
                // 要删除的ID数据
                var id_arr = [];
                if( rows.length>0 && $this[0].tagName != 'A' )
                {
                    // 批量删
                    for(var i=0;i<rows.length;i++)
                    {
                        id_arr[i] = rows[i].id;
                    }
                }
                else
                {
                    // 单删
                    id_arr[0] = row.id;
                }

                // 判断提交的ID，是空为空
                if( id_arr.length<1 )
                {
                    $.Layer.confirm({msg : "<?=Yii::$app->sysLanguage->getTranslateBySymbol('theDeletedDataIsEmpty') ?>", fn : function() { //删除的数据为空
                    }});
                    return;
                }
                // 转换json数据提交
                id_arr = JSON.stringify(id_arr);
                $.Layer.confirm({
                    msg : '<?=Yii::$app->sysLanguage->getTranslateBySymbol('deleteConfirm') ?>', //确认要删除吗
                    fn : function() {
                        $.ajax({
                            type: "post",
                            dataType: "json",
                            cache: false,
                            data: {'_csrf':_csrf, 'id_arr':id_arr},
                            url: "<?=Url::to(['delete']);?>",
                            success: function(data){
                                if( data.code==='T' )
                                {
                                    $.grid.reload();
                                    art.dialog({time: 1, content: data.info,  icon: 'succeed'});
                                }
                                else
                                {
                                    art.dialog({time: 2, content: data.info,  icon: 'error'});
                                }
                            }
                        });
                    }
                });
            });
        });
    })(jQuery);
</script>