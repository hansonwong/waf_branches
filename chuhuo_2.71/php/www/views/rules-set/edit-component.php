<?php
use \yii\helpers\Url;
$defaultRuleTemplate = \app\logic\waf\wafRules\Rules::getDefaultRuleTemplate();
$ruleModelGroup = \app\logic\waf\models\SelectList::ruleModelGroup(false);
$ruleModelGroup = json_encode($ruleModelGroup);
?>
<style>body{padding: 0 5px 5px 5px;}</style>
<div class="btn_box">
    <div class="aearch_box">
        <select id="searchRuleKey">
            <!--输入ID-->
            <option value="realid"><?=Yii::$app->sysLanguage->getTranslateBySymbol('inputId') ?></option>
            <!--输入名称-->
            <option value="name"><?=Yii::$app->sysLanguage->getTranslateBySymbol('typeName') ?></option>
        </select>
        <input type='hidden' name='op' id='op' value='' />
        <input id="searchRuleContent" type="text" class="text" >
        <!--查询-->
        <input type="button" class="btn btn_search" onclick="ruleSearch(false);" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('query') ?>">
        <input name="b_ref" id="b_ref" type="button" class="btn c_b btn_ref" onclick="ruleSearch(true);" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('refresh') ?>">
    </div>
</div>
<div id="maingrid" class="list"></div>

<script type="text/javascript">
    //提交前的操作
    function formSubmitBefore(){
        submitForRules();
    }

    $(function(){
        showGroupModelIdInit();
    });

    //设置rule值
    function ruleSetting(val){
        vueData.val.rule = val;
        $('#field-rule').val(val);
    }

    //初始化选择框是否显示
    function showGroupModelIdInit() {
        vueData.toggle.groupModelId = vueData.val.type == 2;
    }

    var ruleModelGroup = <?=$ruleModelGroup?>;

    // 是否显示所属站点组模板
    function showGroupModelId(th) {
        var groupModelId = $('#field-groupModelId');
        if( $(th).val() == 2 )
        {
            var group = groupModelId.val();
            if('' !== group){
                var rule = ruleModelGroup[group].rule;
                ruleSetting(rule);
            }
        }
        vueData.toggle.groupModelId = $(th).val() == 2;

        $.grid.reload();
    }

    // 切换 所属站点组模板 后，规则选择的情况
    function changeGroupModelId(th) {
        var group = $('#field-groupModelId').val();
        if(null !== group){
            var rule = ruleModelGroup[group].rule;
            ruleSetting(rule);
        }
        $.grid.reload();
    }

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

    //提交前的处理
    function submitForRules(){
        var ruleUnChecked;

        // 判断当前是什么状态提交的, 搜索提交，还是全局提交
        var op = $('#op').val();
        if(op==='search') ruleUnChecked = getSearchRule();
        else ruleUnChecked = getNoSelect();

        var rule = JSON.stringify(ruleUnChecked);
        ruleSetting(rule);
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

    // 获取 摸索 状态下， 重新计算rule的数据
    function getSearchRule() {
        var ruleUnChecked;

        var ruleEle = vueData.val.rule;
        // 由于有些数据不规则，不是字符型，所以统一返字符型
        ruleUnChecked = JSON.parse(ruleEle).map(function(item) {
            return item.toString();
        });

        // 取出未被选中的数据
        var idNoArr = getNoSelect();
        for(var i=0; i<idNoArr.length; i++ )
        {
            if( $.inArray(idNoArr[i], ruleUnChecked) === -1 )
            {
                ruleUnChecked.push(idNoArr[i]);
            }
        }

        // 获取已选中的规则
        var idYesArr = getNoSelect(false);
        // 筛选出未选择的数据出来
        for(var k=0; k<ruleUnChecked.length; k++ )
        {
            if( $.inArray(ruleUnChecked[k],idYesArr) > -1 )
            {
                ruleUnChecked.splice(k,1);
            }
        }

        return ruleUnChecked;
    }

    // 取出未选择或者已选择的数据的数据
    function getNoSelect(type=true) {
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

        // 返回已选择的数组数据
        if( type===false )
        {
            return idArrSelect;
        }

        // 筛选出未选择的数据出来
        var idArr = [];
        for(var k=0; k<idArrAll.length; k++ )
        {
            if( $.inArray(idArrAll[k],idArrSelect) === -1 )
            {
                idArr.push(idArrAll[k]);
            }
        }

        return idArr;
    }

    /**
     * 搜索/刷新
     * @param refresh 是否刷新
     * @param key
     * @param content
     */
    function ruleSearch(refresh, key, content){
        var opEle = $('#op');
        var op = opEle.val(); // 取得之前是否有查找状态
        if( op==='search' )
        {
            var reRule = getSearchRule();
            var rule = JSON.stringify(reRule);
            ruleSetting(rule);
        } else {
            $('#op').val('search'); // 记录当前是查找状态
        }

        if(refresh) opEle.val('');
        else grid.options.newPage = 1;

        var key = refresh ? '' : $('#searchRuleKey').val();
        var content = refresh ? '' : $('#searchRuleContent').val();

        $.grid.options.parms = [];
        $.grid.options.parms.push({name: 'key',value: key});
        $.grid.options.parms.push({name: 'content',value: content});
        $.grid.options.parms.push({name: '_csrf',value: $('meta[name=csrf-token]').attr('content')});

        $.grid.loadData(true);
    }
</script>
