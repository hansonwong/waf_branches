<?php
use \yii\helpers\Url;
use yii\helpers\Html;
?>
<div class="list_page">
    <div class="btn_box" style="height: auto">
        <div class="btn_list">
            <!--加入防误报-->
            <input name="b_add" id="b_add" type="button" class="btn c_g bt_join btn_add" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('addFalseAlarm') ?>">
            <!--导出-->
            <input name="b_stop" id="b_stop" type="button" class="btn c_g btn_exp" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('export') ?>">
            <!--删除-->
            <input name="b_del" id="b_del" type="button" class="btn c_o btn_del" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('delete') ?>">
            <!--清空-->
            <input name="b_open" id="b_open" type="button" class="btn c_o btn_clear" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('empty') ?>">
            <!--刷新-->
            <input name="b_ref" id="b_ref" type="button" class="btn c_b btn_ref" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('refresh') ?>">
        </div>
        <div class="aearch_box" style="margin-top: 5px">
            <form action="" method="post">
                <!--攻击时间-->
                <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('attackTime') ?>：</label>
                <!--开始时间-->
                <input type="text" id="aearchStartDate" name="aearchStartDate" class="text date_plug date_pos" placeholder="<?=Yii::$app->sysLanguage->getTranslateBySymbol('timeStart') ?>"
                       onFocus="var endDate=$dp.$('aearchEndDate');WdatePicker({onpicked:function(){endDate.focus();},
                       maxDate:'#F{$dp.$D(\'aearchEndDate\')}',maxDate:'%y-%M-%d',dateFmt:'yyyy-MM-dd HH:mm:ss'})">
                <!--至-->
                <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('to') ?></label>
                <!--结束时间-->
                <input type="text" id="aearchEndDate" name="aearchEndDate" class="text date_plug date_pos" placeholder="<?=Yii::$app->sysLanguage->getTranslateBySymbol('timeStop') ?>"
                       onFocus="WdatePicker({minDate:'#F{$dp.$D(\'aearchStartDate\')}',maxDate:'%y-%M-%d',dateFmt:'yyyy-MM-dd HH:mm:ss'})">
                <!--查询-->
                <input type="button" class="btn btn_search" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('query') ?>">
                <!--精确查询-->
                <input type="button" class="btn btn_sea" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('queryAccurate') ?>" >
            </form>
        </div>
    </div>

    <div class="keyword_box pad_top" id="keyword_box" style="display:none">
        <form action="" method="post">
            <span class="up" ></span>
            <span class="close"  ></span>
            <ul style="overflow: visible">
                <li>
                    <!--攻击时间-->
                    <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('attackTime') ?>：</label>
                    <!--开始时间-->
                    <input type="text" id="keywordStartDate" name="keywordStartDate" class="text date_plug date_pos"
                           onFocus="var endDate=$dp.$('keywordEndDate');WdatePicker({onpicked:function(){endDate.focus();},
                           maxDate:'#F{$dp.$D(\'keywordEndDate\')}',maxDate:'%y-%M-%d',dateFmt:'yyyy-MM-dd HH:mm:ss'})" placeholder="<?=Yii::$app->sysLanguage->getTranslateBySymbol('timeStart') ?>">
                    <!--至-->
                    <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('to') ?></label>
                    <!--结束时间-->
                    <input type="text" id="keywordEndDate" name="keywordEndDate" class="text date_plug date_pos"
                           onFocus="WdatePicker({minDate:'#F{$dp.$D(\'keywordStartDate\')}',maxDate:'%y-%M-%d',dateFmt:'yyyy-MM-dd HH:mm:ss'})" placeholder="<?=Yii::$app->sysLanguage->getTranslateBySymbol('timeStop') ?>">
                </li>
                <li>
                    <!--攻击类型-->
                    <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('attackType') ?>：</label>
                    <select id="type" name="type" class="text">
                        <!--请选择-->
                        <option value=""><?=Yii::$app->sysLanguage->getTranslateBySymbol('pleaseSelect') ?></option>
                        <?php foreach( $RuleCatArr as $k=>$v ): ?>
                            <option value="<?=$k ?>" title="<?= Html::encode($v) ?>" >
                                <?= Html::encode($v) ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </li>
                <li>
                    <!--危害等级-->
                    <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('hazardGrade') ?>：</label>
                    <select id="Severity" name="Severity">
                        <!--请选择-->
                        <option value="" class="text"><?=Yii::$app->sysLanguage->getTranslateBySymbol('pleaseSelect') ?></option>
                        <?php foreach( $SeverityArr as $k=>$v ): ?>
                            <option value="<?=$k ?>" title="<?= Html::encode($v) ?>" >
                                <?= Html::encode($v) ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </li>
                <li>
                    <!--源IP地址-->
                    <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('sourceIpAddress') ?>：</label>
                    <!--如-->
                    <input name="SourceIP" type="text" class="text" placeholder="<?=Yii::$app->sysLanguage->getTranslateBySymbol('suchAs') ?>：172.0.0.1">
                </li>
                <li>
                    <!--源端口-->
                    <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('sourcePort') ?>：</label>
                    <!--如-->
                    <input name="SourcePort" type="text" class="text" placeholder="<?=Yii::$app->sysLanguage->getTranslateBySymbol('suchAs') ?>：8080">
                </li>
                <li>
                    <!--目标IP-->
                    <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('targetIp') ?>：</label>
                    <!--如-->
                    <input name="DestinationIP" type="text" class="text" placeholder="<?=Yii::$app->sysLanguage->getTranslateBySymbol('suchAs') ?>：172.0.0.1">
                </li>
                <li>
                    <!--目标端口-->
                    <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('destinationPort') ?>：</label>
                    <!--如-->
                    <input name="DestinationPort" type="text" class="text" placeholder="<?=Yii::$app->sysLanguage->getTranslateBySymbol('suchAs') ?>：8080">
                </li>
                <li>
                    <!--拦截方式-->
                    <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('interceptionMode') ?>：</label>
                    <select id="Status" name="Status" class="text">
                        <!--请选择-->
                        <option value=""><?=Yii::$app->sysLanguage->getTranslateBySymbol('pleaseSelect') ?></option>
                        <?php foreach( $ActionCatArr as $k=>$v ): ?>
                            <option value="<?=$k ?>" title="<?= Html::encode($v) ?>">
                                <?= Html::encode($v) ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </li>
                <li>
                    <!--HTTP类型-->
                    <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('httpType') ?>：</label>
                    <select id="HttpMethod" name="HttpMethod" class="text">
                        <!--请选择-->
                        <option value=""><?=Yii::$app->sysLanguage->getTranslateBySymbol('pleaseSelect') ?></option>
                        <?php foreach( $HttpTypeSetArr as $k => $v ): ?>
                            <option value="<?=$v ?>" title="<?= Html::encode($v) ?>" >
                                <?= Html::encode($v) ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </li>
                <li>
                    <!--目标主机-->
                    <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('destinationHost') ?>：</label>
                    <!--如-->
                    <input name="Host" type="text" class="text" placeholder="<?=Yii::$app->sysLanguage->getTranslateBySymbol('suchAs') ?>:www.example.com">
                </li>
                <li>
                    <!--查询-->
                    <input type="button" class="btn bpad btn_sea_search" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('query') ?>">
                </li>
            </ul>
        </form>
    </div>

    <div id="maingrid"  class="list"></div>

</div>
<script type="text/javascript">
    (function ($) {  //避免全局依赖,避免第三方破坏
        $(document).ready(function () {
            var _csrf = $('meta[name=csrf-token]').attr('content');

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
                showJoin:true, //是否加入防误报按钮
                showOutage:true, //是否停用对应规则按钮
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
                detail: {
                    height: 'auto', onShowDetail: function (r, p) {
                        var id = r.id;
                        $.ajax({
                            url: '<?php echo Url::to(['index', 'op' => 'detail']);?>',
                            type: 'POST',
                            dataType: "json",
                            data:{'_csrf':_csrf, 'id':id},
                            cache: false,
                            timeout: 30000,
                            success: function(d){
                                var el = '<table cellpadding="0" cellspacing="0" style="width:95%;" class="detailtd">' +
                                    '<tr>' +
                                    '<td align="right" class="dtd" width="120">' +
                                    '<?=Yii::$app->sysLanguage->getTranslateBySymbol("ruleModule") ?>：' +  //规则模块
                                    '</td>' +
                                    '<td>' + d.ruleCatName + '</td>' +
                                    '</tr>' +
                                    '<tr>' +
                                    '<td align="right" class="dtd">' +
                                    '<?=Yii::$app->sysLanguage->getTranslateBySymbol("rulesName") ?>：' +  //规则名称
                                    '</td>' +
                                    '<td>' + d.name + '</td>' +
                                    '</tr>' +
                                    '<tr>' +
                                    '<td align="right" class="dtd">' +
                                    '<?=Yii::$app->sysLanguage->getTranslateBySymbol("generalInformation") ?>：' + //一般信息
                                    '</td>' +
                                    '<td>' + d.Msg + '</td>' +
                                    '</tr>' +
                                    '<tr>' +
                                    '<td align="right" class="dtd">' +
                                    '<?=Yii::$app->sysLanguage->getTranslateBySymbol("matchingContent") ?>：' +  //匹配内容
                                    '</td>' +
                                    '<td>' + d.MatchData + '</td>' +
                                    '</tr>' +
                                    '<tr>' +
                                    '<td align="right" class="dtd">' +
                                    '<?=Yii::$app->sysLanguage->getTranslateBySymbol("ruleId") ?>：' + //规则ID
                                    '</td>' +
                                    '<td>' + d.RuleID + '</td>' +
                                    '</tr>' +
                                    '<tr>' +
                                    '<td align="right" class="dtd">URL：</td>' +
                                    '<td>' + d.url + '</td>' +
                                    '</tr>' +
                                    '</table>';
                                $(p).append($(el).css('margin', '20px auto'));
                            }
                        });
                    }
                }
            });

            GridTable.on('beforerender', function (e, grid) {
                // 搜索提交
                $('.aearch_box').delegate('input.btn_search', 'click', function () {
                    grid.options.newPage = 1;

                    grid.options.parms = [];
                    grid.options.parms.push({name: 'LogDateTimeStart',value: $('input[name=aearchStartDate]').val()});
                    grid.options.parms.push({name: 'LogDateTimeEnd',value: $('input[name=aearchEndDate]').val()});
                    grid.options.parms.push({name: '_csrf',value: _csrf});

                    grid.loadData(true);
                });

                // 精确查询
                $('.keyword_box').delegate('input.btn_sea_search', 'click', function () {
                    grid.options.newPage = 1;

                    grid.options.parms = [];
                    grid.options.parms.push({name: '_csrf',value: _csrf});
                    grid.options.parms.push({name: 'keywordStartDate',value: $('input[name=keywordStartDate]').val()}); // 攻击时间
                    grid.options.parms.push({name: 'keywordEndDate',value: $('input[name=keywordEndDate]').val()}); // 攻击时间
                    grid.options.parms.push({name: 'type',value: $('#type').find('option:selected').val()}); // 攻击类型
                    grid.options.parms.push({name: 'Severity',value: $('#Severity').find('option:selected').val()}); // 危害等级
                    grid.options.parms.push({name: 'SourceIP',value: $('input[name=SourceIP]').val()}); // 源IP地址
                    grid.options.parms.push({name: 'SourcePort',value: $('input[name=SourcePort]').val()}); // 源端口
                    grid.options.parms.push({name: 'DestinationIP',value: $('input[name=DestinationIP]').val()}); // 目标IP
                    grid.options.parms.push({name: 'DestinationPort',value: $('input[name=DestinationPort]').val()}); // 目标端口
                    grid.options.parms.push({name: 'Status',value: $('#Status').find('option:selected').val()}); // 拦截方式
                    grid.options.parms.push({name: 'HttpMethod',value: $('#HttpMethod').find('option:selected').val()}); //HTTP类型
                    grid.options.parms.push({name: 'Host',value: $('input[name=Host]').val()}); // 目标主机

                    grid.loadData(true);
                });
            });

            // 刷新
            $('.list_page').on('click', 'input.btn_ref', function(e) {
                e.preventDefault();
                $.grid.options.newPage = 1;
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
                    $.Layer.confirm({msg : top.translation.t('selectdataToDelete') + '?', fn : function() {  //请选择要删除的数据
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
                    $.Layer.confirm({msg : top.translation.t('theDeletedDataIsEmpty'), fn : function() {  //删除的数据为空
                    }});
                    return;
                }
                // 转换json数据提交
                id_arr = JSON.stringify(id_arr);
                $.Layer.confirm({
                    msg : top.translation.t('isDeleteData'),  //是否要删除数据
                    fn : function() {
                        $.ajax({
                            type: "post",
                            dataType: "json",
                            cache: false,
                            data: {'_csrf':_csrf, 'id_arr':id_arr},
                            url: "<?=Url::to(['delete']);?>",
                            success: function(data){
                                if(data.code === 'T')
                                {
                                    $.grid.reload();
                                    /* 删除数据后移除全选复选框勾选状态*/
                                    document.querySelectorAll('.l-grid-hd-row')[1].className = 'l-grid-hd-row';

                                    art.dialog({icon: 'succeed', content: data.info, time: 1});
                                }
                                else
                                {
                                    art.dialog({icon: 'error', content: data.info, time: 2});
                                }
                            }
                        });
                    }
                });
            });

            //加入防误报
            $('.list_page').on('click', 'input.bt_join,a.bt_join', function(e) {
                e.preventDefault();
                var $this = $(this);
                var rows = $.grid.getSelectedRows();//批量获取对象组
                var row = $.grid.getRow($this.attr('rowid'));//获取单个对象

                // 判断是不是按了多行选择
                if( !rows.length>0 && $this[0].tagName == 'INPUT' )
                {
                    $.Layer.confirm({msg : top.translation.t('selectAddFalseAlarmData')+'?', fn : function() {  //选择加入防误报的数据
                    }});
                    return;
                }
                // 要加入的ID数据
                var id_arr = [];
                if( rows.length>0 && $this[0].tagName != 'A' )
                {
                    // 批量
                    for(var i=0;i<rows.length;i++)
                    {
                        id_arr[i] = rows[i].id;
                    }
                }
                else
                {
                    // 单个
                    id_arr[0] = row.id;
                }

                // 判断提交的ID，是空为空
                if( id_arr.length<1 )
                {
                    $.Layer.confirm({msg : top.translation.t('noChoiceNeedsToBeAddedToMisinformation'), fn : function() {  //加入防误报的数据为空
                    }});
                    return;
                }
                // 转换json数据提交
                id_arr = JSON.stringify(id_arr);
                $.Layer.confirm({
                    msg : top.translation.t('isAddFalseAlarm')+'?',  //是否加入防误报
                    fn : function() {
                        $.ajax({
                            type: "post",
                            dataType: "json",
                            cache: false,
                            data: {'_csrf':_csrf, 'id_arr':id_arr},
                            url: "<?=Url::to(['update', 'op'=>'addFwb']);?>",  // addFwb
                            success: function(data){
                                if(data.code === 'T')
                                {
                                    $.grid.reload();
                                    /* 删除数据后移除全选复选框勾选状态*/
                                    document.querySelectorAll('.l-grid-hd-row')[1].className = 'l-grid-hd-row';

                                    art.dialog({icon: 'succeed', content: data.info, time: 1});
                                }
                                else
                                {
                                    art.dialog({icon: 'error', content: data.info, time: 2});
                                }
                            }
                        });
                    }
                });
            });

            // 停用对应规则
            $('.list_page').on('click', 'a.bt_outage', function(e) {
                e.preventDefault();
                var row = $.grid.getRow($(this).attr('rowid'));//获取单个对象
                var id = row.id;

                // 判断提交的ID，是空为空
                if( id.length<1 )
                {
                    $.Layer.confirm({msg : top.translation.t('stopRulesDataIsNull'), fn : function() {  }});  //停用对应规则数据为空
                    return;
                }
                $.Layer.confirm({
                    msg : top.translation.t('isStopRules')+'?',  //是否停用对应规则
                    fn : function() {
                        $.ajax({
                            type: "post",
                            dataType: "json",
                            cache: false,
                            data: {'_csrf':_csrf, 'id':id},
                            url: "<?=Url::to(['update', 'op'=>'stopRule']);?>",
                            success: function(data){
                                if(data.code === 'T')
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
                    }
                });
            });

            // 清空
            $('.list_page').delegate('.btn_clear', 'click', function () {
                $.Layer.confirm({
                    //title: '系统友情提示', msg:'<span class="red">'+'清空操作将对目前所有数据进行清空，清空后将不能恢复,确认?'+'</span>',
                    title: top.translation.t('systemFriendlyTips'), msg:'<span class="red">'+top.translation.t('OutLinkLogEmptyTips')+'?'+'</span>',
                    fn: function () {
                        // 攻击时间，优先使用精确查询 时间
                        var LogDateTimeStart = $('input[name=aearchStartDate]').val(); // 攻击时间
                        var LogDateTimeEnd = $('input[name=aearchEndDate]').val(); // 攻击时间

                        var keywordStartDate = $('input[name=keywordStartDate]').val(); // 攻击时间
                        if( keywordStartDate.trim().length<1 )
                        {
                            keywordStartDate = LogDateTimeStart;
                        }
                        var keywordEndDate = $('input[name=keywordEndDate]').val(); // 攻击时间
                        if( keywordEndDate.trim().length<1 )
                        {
                            keywordEndDate = LogDateTimeEnd;
                        }

                        var type = $('#type').find('option:selected').val(); // 攻击类型
                        var Severity = $('#Severity').find('option:selected').val(); // 危害等级
                        var SourceIP = $('input[name=SourceIP]').val(); // 源IP地址
                        var SourcePort = $('input[name=SourcePort]').val(); // 源端口
                        var DestinationIP = $('input[name=DestinationIP]').val(); // 目标IP
                        var DestinationPort = $('input[name=DestinationPort]').val(); // 目标端口
                        var Status = $('#Status').find('option:selected').val(); // 拦截方式
                        var HttpMethod = $('#HttpMethod').find('option:selected').val(); //HTTP类型
                        var Host = $('input[name=Host]').val(); // 目标主机

                        var searchData = {
                            'keywordStartDate':keywordStartDate, 'keywordEndDate':keywordEndDate, 'type':type,
                            'Severity':Severity, 'SourceIP':SourceIP, 'SourcePort':SourcePort, 'DestinationIP':DestinationIP,
                            'DestinationPort':DestinationPort, 'Status':Status, 'HttpMethod':HttpMethod, 'Host':Host
                        };
                        searchData = JSON.stringify(searchData);

                        $.ajax({
                            type: "post",
                            dataType: "json",
                            cache: false,
                            data: {'_csrf':_csrf, 'searchData':searchData},
                            url: "<?=Url::to(['delete', 'op'=>'dump']);?>",
                            success: function(data){
                                if(data.code === 'T')
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
                    }
                });
            });

            // 导出
            $('.list_page').delegate('.btn_exp', 'click', function () {
                $.Layer.confirm({
                    //title: '系统友情提示', msg:'提示:  将根据当前条件导出日志,最多导出最新的20000条记录.',
                    title: top.translation.t('systemFriendlyTips'), msg:top.translation.t('OutLinkLogExportTips'),
                    fn: function () {
                        // 攻击时间，优先使用精确查询 时间
                        var LogDateTimeStart = $('input[name=aearchStartDate]').val(); // 攻击时间
                        var LogDateTimeEnd = $('input[name=aearchEndDate]').val(); // 攻击时间

                        var keywordStartDate = $('input[name=keywordStartDate]').val(); // 攻击时间
                        if( keywordStartDate.trim().length<1 )
                        {
                            keywordStartDate = LogDateTimeStart;
                        }
                        var keywordEndDate = $('input[name=keywordEndDate]').val(); // 攻击时间
                        if( keywordEndDate.trim().length<1 )
                        {
                            keywordEndDate = LogDateTimeEnd;
                        }

                        var type = $('#type').find('option:selected').val(); // 攻击类型
                        var Severity = $('#Severity').find('option:selected').val(); // 危害等级
                        var SourceIP = $('input[name=SourceIP]').val(); // 源IP地址
                        var SourcePort = $('input[name=SourcePort]').val(); // 源端口
                        var DestinationIP = $('input[name=DestinationIP]').val(); // 目标IP
                        var DestinationPort = $('input[name=DestinationPort]').val(); // 目标端口
                        var Status = $('#Status').find('option:selected').val(); // 拦截方式
                        var HttpMethod = $('#HttpMethod').find('option:selected').val(); //HTTP类型
                        var Host = $('input[name=Host]').val(); // 目标主机

                        var _url = "<?=Url::to(['export-data']);?>"+
                            "&keywordStartDate="+keywordStartDate+
                            "&keywordEndDate="+keywordEndDate+
                            "&type="+type+
                            "&Severity="+Severity+
                            "&SourceIP="+SourceIP+
                            "&SourcePort="+SourcePort+
                            "&DestinationIP="+DestinationIP+
                            "&DestinationPort="+DestinationPort+
                            "&Status="+Status+
                            "&HttpMethod="+HttpMethod+
                            "&Host="+Host;
                        window.location.href = _url;
                    }
                });
            });

        });
    })(jQuery);
</script>

