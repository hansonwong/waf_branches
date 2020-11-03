<?php
use \yii\helpers\Url;
$defaultRuleTemplate = \app\logic\waf\wafRules\Rules::getDefaultRuleTemplate();
?>
<style>body{padding: 0 5px 5px 5px;}</style>
<div id="maingrid" class="list"></div>

<script type="text/javascript">

    // 分组 全选与取消
    function checkAllGroup(th) {
        // 判断当前是否选中
        var check = $(th).is(':checked');
        var realid = $(th).val();

        // 获取组结点
        var groupRow = $(th).parent().parent();
        var currentRow = groupRow.next(".l-grid-row,.l-grid-totalsummary-group,.l-grid-detailpanel");
        // 循环向 标签加入选中类
        while (true)
        {
            if (currentRow.length === 0) break;

            if( check ) {
                currentRow.addClass("l-selected");
            }
            else
            {
                currentRow.removeClass("l-selected");
            }
            currentRow = currentRow.next(".l-grid-row,.l-grid-totalsummary-group,.l-grid-detailpanel");
        }

        // 把选中的数据向$.grid加入
        var realidArr = realid.split(',');
        for(var i=0; i<realidArr.length; i++ )
        {
            // 选中
            if( check )
            {
                for( var j=0; j<$.grid.rows.length; j++ )
                {
                    if( $.grid.rows[j].realid === realidArr[i] )
                    {
                        // 判断已选中的有没有在里面
                        var counter = 0;
                        for( var l=0; l<$.grid.selected.length; l++ )
                        {
                            if( $.grid.selected[l].realid === realidArr[i] )
                            {
                                counter++;
                            }
                        }
                        if( counter === 0 )
                        {
                            $.grid.selected.push($.grid.rows[j]);
                        }
                    }
                }
            }
            else
            {
                // 去掉选中的
                for( var k=0; k<$.grid.selected.length; k++ )
                {
                    if( $.grid.selected[k].realid === realidArr[i] )
                    {
                        $.grid.selected.splice(k,1);
                        break;
                    }
                }
            }
        }
    }

    function submitForRules(){
        //选取所有内置规则数据
        var idArrAll = [];
        var rows = $.grid.getData();//批量获取对象组
        for(var i=0;i<rows.length;i++)
        {
            idArrAll.push(String(rows[i].realid));
        }

        // 已选中的数据
        var idArrSelect = [];
        rows = $.grid.getSelectedRows();//批量获取对象组
        for(var j=0;j<rows.length;j++)
        {
            idArrSelect.push(String(rows[j].realid));
        }

        // 取出未选中的
        var idArr = [];
        for(var k=0; k<idArrAll.length; k++ )
        {
            if( $.inArray(idArrAll[k],idArrSelect) === -1 )
            {
                idArr.push(idArrAll[k]);
            }
        }
        vueData.val.rule = JSON.stringify(idArr);
        $('#rule').val(idArr);
    }


    (function ($) {  //避免全局依赖,避免第三方破坏

        $(document).ready(function () {
            var _csrf = $('meta[name=csrf-token]').attr('content');

            // 判断数据表格初始化时，是否被选中
            function GridIsChecked(rowData)
            {
                // 记录所有未被选中的数据
                var ruleAllArr = [];

                var rules = vueData.val.rule;

                if(null == rules || '' == rules) rules = '<?=$defaultRuleTemplate->rule?>';

                // 由于有些数据不规则，不是字符型，所以统一返字符型
                var ruleArr = JSON.parse(rules).map(function(item) {
                    return item.toString();
                });
                ruleAllArr.push.apply(ruleAllArr, ruleArr);

                // 判断当前行规则realid，是否在 rule规则里, 不存在就返回选中
                if( $.inArray(rowData.realid,ruleAllArr) === -1 )
                {
                    return true;
                }
                
                return false;
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
                width: '100%',
                height: '600px',
                usePager: false,
                pageSize: 20,
                pageSizeOptions: [10, 20, 30, 40, 50, 100],
                showRuning: false,
                checkbox: true,
                isChecked: GridIsChecked, // 初始化选择行 函数               
                groupColumnName: 'sTypeName',//分组名称
                groupRender: function (sTypeName, groupdata){
                    var realid = [];
                    groupdata.forEach(function (value) {
                        realid.push(value.realid);
                    });
                    var realidStr = realid.join(",");
                    return ' <input type="checkbox" value='+realidStr+' onclick="checkAllGroup(this);"> ' + sTypeName + '';
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

        });
    })(jQuery);
</script>
