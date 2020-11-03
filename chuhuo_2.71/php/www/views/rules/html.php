<?php
use \yii\helpers\Url;
?>
<script>
    hListTabelConfig.showSitting = false;//是否需要操作列
    hListTabelConfig.showEdit = false;
    hListTabelConfig.showView = false;
    hListTabelConfig.showDel = false;
    hListTabelConfig.showLock = false;//是否需要解锁和锁定状态栏
    hListTabelConfig.isSelectR = true;//复选按钮是否选中
    hListTabelConfig.showSetting = true;//是否显示配置按钮
    hListTabelConfig.allowHideColumn = false;//是否显示'切换列层'按钮
    hListTabelConfig.usePager = false;//不分页
    hListTabelConfig.groupColumnName = 'typeName';//分组名称
    hListTabelConfig.showRuning = false;
    hListTabelConfig.checkbox = true;
    hListTabelConfig.rowAttrRender = function (rowdata,rowid){
        if( rowdata.isWhere === 1 ) return;
        return "style='display: none;'";
    };
    hListTabelConfig.onAfterShowData = function (currentData) {
        if( currentData.isWhere === 1 ) return;
        var gridWidth = $('.l-grid-header-inner').width();
        $('.l-grid-grouprow-cell').attr('style','width: '+gridWidth+'px;');
        $('.l-grid-grouprow-cell span').addClass('l-grid-group-togglebtn-close');
    };
    hListTabelConfig.groupRender = function (sTypeName, groupdata) {
        var realid = [];
        groupdata.forEach(function (value) {
            realid.push(value.realid);
        });
        var realidStr = realid.join(",");
        return ' <input type="checkbox" value=' + realidStr + ' onclick="checkAllGroup(this);"> ' + sTypeName + '';
    };
    hListTabelConfig.detail = {
        height: 'auto', onShowDetail: function (r, p) {
            var id = r.primaryKey;
            $.ajax({
                url: '<?php echo Url::to(['index', 'op' => 'detail']);?>',
                type: 'POST',
                dataType: "json",
                data: {'_csrf': $('[name=_csrf]').val(), 'id': id},
                cache: false,
                timeout: 30000,
                success: function (d) {
                    var el = '<table cellpadding="0" cellspacing="0" style="width:95%;" class="detailtd">' +
                        '<tr>' +
                        '<td align="right" class="dtd" style="width: 100px">' +
                        top.translation.t('ruleId') +  //规则ID
                        '</td>' +
                        '<td>' + d.realid + '</td>' +
                        '<td align="right" class="dtd" style="width: 100px">' +
                        top.translation.t('category') + //类别
                        '</td>' +
                        '<td>' + d.ruleCatName + '</td>' +
                        '</tr>' +
                        '<tr>' +
                        '<td align="right" class="dtd">' +
                        top.translation.t('rulesName') +  //规则名称
                        '</td>' +
                        '<td colspan="3">' + d.name + '</td>' +
                        '</tr>' +
                        '<tr>' +
                        '<td align="right" class="dtd">' +
                        top.translation.t('interceptionMode') + //拦截方式
                        '</td>' +
                        '<td>' + d.actionCatName + '</td>' +
                        '<td align="right" class="dtd">' +
                        top.translation.t('sublist') + //告警等级
                        '</td>' +
                        '<td>' + d.warn + '</td>' +
                        '</tr>' +
                        '<tr>' +
                        '<td align="right" class="dtd">' +
                        top.translation.t('isItEnabled') +  // 是否启用
                        '</td>' +
                        '<td colspan="3">' + d.statusStr + '</td>' +
                        '</tr>' +
                        '<tr>' +
                        '<td align="right" class="dtd">' +
                        top.translation.t('remarks') +  //备注
                        '</td>' +
                        '<td colspan="3">' + d.desc + '</td>' +
                        '</tr>' +
                        '<tr>' +
                        '<td align="right" class="dtd">' +
                        top.translation.t('hazardDescription') +  //危害描述
                        '</td>' +
                        '<td colspan="3">' + d.harm_desc + '</td>' +
                        '</tr>' +
                        '<tr>' +
                        '<td align="right" class="dtd">' +
                        top.translation.t('solutionSuggestion') +  //解决建议
                        '</td>' +
                        '<td colspan="3">' + d.suggest + '</td>' +
                        '</tr>' +
                        '</table>';
                    $(p).append($(el).css('margin', '20px auto'));
                }
            });
        }
    };


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
                        $.grid.selected.push($.grid.rows[j]);
                        break;
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
</script>