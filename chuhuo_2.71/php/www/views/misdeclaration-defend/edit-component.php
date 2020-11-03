<?php
use \yii\helpers\Url;
?>
<style>body{padding: 0 5px 5px 5px;}</style>
<div class="btn_box">
    <div class="aearch_box">
        <select name="key" id="key">
            <!--输入ID-->
            <option value="realid"><?=Yii::$app->sysLanguage->getTranslateBySymbol('inputId') ?></option>
            <!--输入名称-->
            <option value="name"><?=Yii::$app->sysLanguage->getTranslateBySymbol('typeName') ?></option>
        </select>
        <input name="content" id="content" type="text" class="text" >
        <!--查询-->
        <input type="button" class="btn btn_search" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('query') ?>">
        <input name="b_ref" id="b_ref" type="button" class="btn c_b btn_ref" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('refresh') ?>">
    </div>
</div>
<div id="maingrid"  class="list"></div>

<script>
    //设置realruleid值
    function realruleidSetting(val){
        vueData.val.realruleid = val;
        $('#field-realruleid').val(val);
    }
</script>

<script>
    (function ($) {  //避免全局依赖,避免第三方破坏
        // 单个选择 复选框事件
        function CheckRow(checked,data,rowid,rowdata)
        {
            // 选中状态
            if( checked === true )
            {
                // 移除所有之上的被选中的 与 所有之下的被选中的
                $(rowdata).prevAll('.l-grid-row').removeClass("l-selected");
                $(rowdata).nextAll('.l-grid-row').removeClass("l-selected");

                // 写入数据
                realruleidSetting(data.realid);

                // 重写 grid.selected数据
                $.grid.selected = [];
                $.grid.selected.push(data);
            }
            else
            {
                $.grid.selected = [];
                realruleidSetting('');
            }
        }

        $(document).ready(function () {
            var _csrf = $('meta[name=csrf-token]').attr('content');

            // 判断数据表格初始化时，是否被选中
            function GridIsChecked(rowData)
            {
                // 记录当前的 realruleid
                var realRuleIdArr = [];

                var realruleid = $('#field-realruleid').val();

                // 空的就没有选择
                if( realruleid.length<1 )
                {
                    return false;
                }

                // ["981143"]
                realRuleIdArr.push(realruleid);

                // 判断当前行规则realid，是否在 realruleid里, 不存在就返回不选中
                if( $.inArray(rowData.realid, realRuleIdArr) === -1 )
                {
                    return false;
                }

                return true;
            }
            /*调用*/
            var GridTable = $.BDGrid({
                _csrf: _csrf,
                sColumnsUrl: "<?php echo Url::to(['rules-set/index', 'op' => 'headerRule']);?>",
                ajax: {
                    url: "<?php echo Url::to(['rules-set/index', 'op' => 'bodyRule']);?>",
                    type: 'POST',
                    parms: {_csrf:_csrf} // yii2需要传的参数
                },
                el: '#maingrid',
                dataAction: 'local', //'local',
                showSitting: false,//是否需要操作列
                showEdit: true,
                showView: true,
                showDel: true,
                showLock: false,//是否需要解锁和锁定状态栏
                isSelectR: true,//复选按钮是否选中
                showSetting:true, //是否显示配置按钮
                root: 'data',//数据
                pageParmName:'page',//页码
                pagesizeParmName:'pagesize',//页数据量
                record: 'total',//总数
                width: '99.8%',
                height: '100%',
                usePager: false,
                pageSize: 20,
                pageSizeOptions: [10, 20, 30, 40, 50, 100],
                showRuning: false,
                checkbox: true,
                isChecked: GridIsChecked, // 初始化选择行 函数
                onCheckRow: CheckRow, // 选择事件(复选框)
                //onCheckAllRow : CheckAllRow , // 选择事件(复选框 全选/全不选)
                groupColumnName: 'sTypeName',//分组名称
                groupRender: function (sTypeName, groupdata){
                    return '' +  sTypeName + '';
                },
                rowAttrRender: function (rowdata,rowid){
                    if( rowdata.isWhere === 1 ) return;
                    return "style='display: none;'";
                },
                onAfterShowData: function (currentData) {
                    if( currentData.isWhere === 1 ) return;
                    var gridWidth = $('.l-grid-header-inner').width();
                    $('.l-grid-grouprow-cell').attr('style','width: '+gridWidth+'px;');
                    $('.l-grid-grouprow-cell span').addClass('l-grid-group-togglebtn-close');
                },
                columnDefs: [   // change
                    {
                        targets: 'name',
                        data: 'name',
                        render: function(row, bVisible, value) {
                            var aa=$('.l-grid2 tr').eq(0).find('td').eq(2).width()-38;
                            return '<div class="rulesName" style="width'+ aa +'px">'+value+'</div>';
                        }
                    }
                ]
            });

            GridTable.on('beforerender', function (e, grid) {
                // 搜索提交

                $('.aearch_box').delegate('input.btn_search', 'click', function () {
                    grid.options.newPage = 1;

                    grid.options.parms = [];
                    grid.options.parms.push({name: 'key',value: $('#key option:selected').val()});
                    grid.options.parms.push({name: 'content',value: $('input[name=content]').val()});
                    grid.options.parms.push({name: '_csrf',value: _csrf});

                    grid.loadData(true);
                });

                // 刷新
                $('.aearch_box').delegate('input.btn_ref', 'click', function(e) {
                    $("#content").val('');  // 重置搜索内容

                    $.grid.options.parms = [];
                    $.grid.options.parms.push({name: 'key',value: ''});
                    $.grid.options.parms.push({name: 'content',value: ''});
                    $.grid.options.parms.push({name: '_csrf',value: _csrf});

                    $.grid.loadData(true);
                });
            });
        });
    })(jQuery);
</script>