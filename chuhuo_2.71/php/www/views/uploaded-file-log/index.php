<?php
use \yii\helpers\Url;
use yii\helpers\Html;
?>
<div class="list_page">
    <div class="btn_box">
        <div class="btn_list"> 
            <!--导出-->
            <input name="b_stop" id="b_stop" type="button" class="btn c_g btn_exp" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('export') ?>">
            <!--删除-->
            <input name="b_del" id="b_del" type="button" class="btn c_o btn_del" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('delete') ?>">
            <!--清空-->
            <input name="b_open" id="b_open" type="button" class="btn c_o btn_clear" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('empty') ?>">
            <!--刷新-->
            <input name="b_ref" id="b_ref" type="button" class="btn c_b btn_ref" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('refresh') ?>">
        </div>
        <div class="aearch_box">
        <form action="" method="post">
            <!--报告时间-->
            <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('reportingTime') ?>：</label>
            <!--开始时间-->
            <input type="text" id="reportStartDate" name="reportStartDate" class="text date_plug date_pos"  
				onFocus="var reportEndDate=$dp.$('reportEndDate');WdatePicker({onpicked:function(){reportEndDate.focus();},
				maxDate:'#F{$dp.$D(\'reportEndDate\')}',maxDate:'%y-%M-%d',dateFmt:'yyyy-MM-dd HH:mm:ss'})" placeholder="<?=Yii::$app->sysLanguage->getTranslateBySymbol('timeStart') ?>">
            <!--至-->
            <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('to') ?></label>
            <!--结束时间-->
			<input type="text" id="reportEndDate" name="reportEndDate" class="text date_plug date_pos"  
				onFocus="WdatePicker({minDate:'#F{$dp.$D(\'reportStartDate\')}',
				maxDate:'%y-%M-%d',dateFmt:'yyyy-MM-dd HH:mm:ss'})" placeholder="<?=Yii::$app->sysLanguage->getTranslateBySymbol('timeStop') ?>">
            <!--查询-->
            <input name="" type="button" class="btn btn_search" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('query') ?>">
            <!--精确查询-->
            <input type="button" class="btn btn_sea" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('queryAccurate') ?>" >
        </form>
        </div>        
    </div>

    <div class="keyword_box pad_top" id="keyword_box" style="display:none">
        <form action="" method="post">
         <span class="up" ></span>
         <span class="close"  ></span>
         <ul>
             <li>
                 <!--报告时间-->
                <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('reportingTime') ?>：</label>
                 <!--开始时间-->
                <input type="text" id="kReportStartDate" name="kReportStartDate" class="text date_plug date_pos"  
				onFocus="var kReportEndDate=$dp.$('kReportEndDate');WdatePicker({onpicked:function(){kReportEndDate.focus();},
				maxDate:'#F{$dp.$D(\'kReportEndDate\')}',maxDate:'%y-%M-%d',dateFmt:'yyyy-MM-dd HH:mm:ss'})" placeholder="<?=Yii::$app->sysLanguage->getTranslateBySymbol('timeStart') ?>">
                 <!--至-->
                 <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('to') ?></label>
                 <!--结束时间-->
                 <input type="text" id="kReportEndDate" name="kReportEndDate" class="text date_plug date_pos"
				onFocus="WdatePicker({minDate:'#F{$dp.$D(\'kReportStartDate\')}',
				maxDate:'%y-%M-%d',dateFmt:'yyyy-MM-dd HH:mm:ss'})"  placeholder="<?=Yii::$app->sysLanguage->getTranslateBySymbol('timeStop') ?>">
             </li>
             <li>
                 <!--上传时间-->
                <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('uploadTime') ?>：</label>
                 <!--开始时间-->
                <input type="text" id="kUploadStartDate" name="kUploadStartDate" class="text date_plug date_pos"  
				onFocus="var kUploadEndDate=$dp.$('kUploadEndDate');WdatePicker({onpicked:function(){kUploadEndDate.focus();},
				maxDate:'#F{$dp.$D(\'kUploadEndDate\')}',maxDate:'%y-%M-%d',dateFmt:'yyyy-MM-dd HH:mm:ss'})" placeholder="<?=Yii::$app->sysLanguage->getTranslateBySymbol('timeStart') ?>">
                 <!--至-->
                 <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('to') ?></label>
                 <!--结束时间-->
				<input type="text" id="kUploadEndDate" name="kUploadEndDate" class="text date_plug date_pos"  
				onFocus="WdatePicker({minDate:'#F{$dp.$D(\'kUploadStartDate\')}',
				maxDate:'%y-%M-%d',dateFmt:'yyyy-MM-dd HH:mm:ss'})"  placeholder="<?=Yii::$app->sysLanguage->getTranslateBySymbol('timeStop') ?>">
             </li>                      
             <li>
                 <!--站点URL-->
                 <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('siteUrl') ?>：</label>
                 <input name="URL" type="text" class="text" placeholder="">
             </li>
             <li>
                 <!--文件名-->
                 <label><?=Yii::$app->sysLanguage->getTranslateBySymbol('fileName') ?>：</label>
                 <input name="filename" type="text" class="text" placeholder="">
             </li>
             <!--查询-->
             <li><input name="" type="button" class="btn btn_sea_search" value="<?=Yii::$app->sysLanguage->getTranslateBySymbol('query') ?>"></li>
         </ul>        
        </form>
    </div>

    <div id="maingrid"  class="list"></div>

</div>
<script type="text/javascript">
    (function ($) {  //避免全局依赖,避免第三方破坏
        $(document).ready(function () {
            var _csrf = $('meta[name=csrf-token]').attr('content');

			var fnOpertion = function(row, rowindex, value)
			{
				var h = '';
				h += '<a href="javascript:;" title="<?=Yii::$app->sysLanguage->getTranslateBySymbol("see") ?>" class="bt_view list-btn" rowid="'+rowindex+'"></a>&nbsp;'; //查看
				return h;
			};
			
			var fnFormatTime = function(row, index, value){
				date = new Date(value*1000);
				Y = date.getFullYear() + '-';
				M = (date.getMonth()+1 < 10 ? '0'+(date.getMonth()+1) : date.getMonth()+1) + '-';
				D = (date.getDate()<10? '0'+date.getDate():date.getDate()) + ' ';
				h = (date.getHours()<10? '0'+date.getHours():date.getHours()) + ':';
				m = (date.getMinutes()<10? '0'+date.getMinutes():date.getMinutes()) + ':';
				s = (date.getSeconds()<10? '0'+date.getSeconds():date.getSeconds());
				return Y+M+D+h+m+s;
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
                showJoin:true, //是否加入防误报按钮
                showOutage:true, //是否停用对应规则按钮
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
				columnDefs: [
					{
						targets: 'iRating',
						data: 'rating',
						render: function (row, bVisible, value){
                            var str;
                            if(value === 'High'){
							    // 高
								str = '<font class="red"><?=Yii::$app->sysLanguage->getTranslateBySymbol("high") ?></font>';
							}else if(value === 'Low') {
							    // 低
								str = '<font class="green"><?=Yii::$app->sysLanguage->getTranslateBySymbol("low") ?></font>';
							}
							return str;                             
						}
					},
					
					{
						targets: 'iView',
						data: 'view',
						render: fnOpertion
					},
					
					{
						targets: 'iReportTime',
						data: 'reporttime',
						render: fnFormatTime
					},
					
					{
						targets: 'iUploadTime',
						data: 'uploadtime',
						render: fnFormatTime
					}
				]
                
            });

            GridTable.on('beforerender', function (e, grid) {
                // 搜索提交
                $('.aearch_box').delegate('input.btn_search', 'click', function () {
                    grid.options.newPage = 1;

                    grid.options.parms = [];
                    grid.options.parms.push({name: 'reportStartDate',value: $('input[name=reportStartDate]').val()});
                    grid.options.parms.push({name: 'reportEndDate',value: $('input[name=reportEndDate]').val()});
                    grid.options.parms.push({name: '_csrf',value: _csrf});

                    grid.loadData(true);
                });

                // 精确查询
                $('.keyword_box').delegate('input.btn_sea_search', 'click', function () {
                    grid.options.newPage = 1;

                    grid.options.parms = [];
                    grid.options.parms.push({name: '_csrf',value: _csrf});
                    grid.options.parms.push({name: 'kReportStartDate',value: $('input[name=kReportStartDate]').val()}); //报告时间
                    grid.options.parms.push({name: 'kReportEndDate',value: $('input[name=kReportEndDate]').val()}); //报告时间
                    grid.options.parms.push({name: 'kUploadStartDate',value: $('input[name=kUploadStartDate]').val()}); // 上传时间
                    grid.options.parms.push({name: 'kUploadEndDate',value: $('input[name=kUploadEndDate]').val()}); // 上传时间
                    grid.options.parms.push({name: 'URL',value: $('input[name=URL]').val()}); // URL
                    grid.options.parms.push({name: 'filename',value: $('input[name=filename]').val()}); // 文件名

                    grid.loadData(true);
                });
            });

            // 刷新
            $('.list_page').on('click', 'input.btn_ref', function(e) {
                e.preventDefault();

                $.grid.options.newPage = 1;

                $.grid.reload();
            });
			
			//查看
			GridTable.on('view', function (e, c, table, data) {
				e.preventDefault();
				if (data.length == 1) {
					var dialog = $.Layer.iframe({
					id: 'report_iframe',
					title: false,
					url: '<?php echo Url::to(['view']);?>&id='+data[0]['id'],
					button: false,
					cancel: false,
					width: 650,
					height: 500
					});
					dialog.hData = data[0];
					dialog.hGrid = table;
					
				} else {
					$.Layer.confirm({
						title:'<?=Yii::$app->sysLanguage->getTranslateBySymbol("fileAnalysisResultsShow") ?>',  //文件分析结果-展示
						msg: '<?=Yii::$app->sysLanguage->getTranslateBySymbol("selectOneRowData") ?>？', fn: function () {  //请选择某一行数据
						}
					});
				}
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
                    $.Layer.confirm({msg : '<?=Yii::$app->sysLanguage->getTranslateBySymbol("selectdataToDelete") ?>？', fn : function() {  //请选择要删除的数据
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
                    $.Layer.confirm({msg : '<?=Yii::$app->sysLanguage->getTranslateBySymbol("theDeletedDataIsEmpty") ?>', fn : function() {  //删除的数据为空
                    }});
                    return;
                }
                // 转换json数据提交
                id_arr = JSON.stringify(id_arr);
                $.Layer.confirm({
                    msg : '<?=Yii::$app->sysLanguage->getTranslateBySymbol("isDeleteData") ?>？',  //是否要删除数据
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
                    // 系统友情提示  清空操作将对目前查询条件所列数据进行清空，清空后将不能恢复,确认?
                    title: '<?=Yii::$app->sysLanguage->getTranslateBySymbol("systemFriendlyTips") ?>', msg:'<span class="red">'+'<?=Yii::$app->sysLanguage->getTranslateBySymbol("OutLinkLogEmptyTips") ?>?'+'</span>',
                    fn: function () {
                        $.ajax({
                            type: "post",
                            dataType: "json",
                            cache: false,
                            data: {'_csrf':_csrf},
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
                    //系统友情提示  提示:  将根据当前条件导出日志,最多导出最新的20000条记录.
                    title: '<?=Yii::$app->sysLanguage->getTranslateBySymbol("systemFriendlyTips") ?>', msg:'<?=Yii::$app->sysLanguage->getTranslateBySymbol("OutLinkLogExportTips") ?>',
                    fn: function () {
                        // 攻击时间，优先使用精确查询 时间
                        var reportStartDate = $('input[name=reportStartDate]').val(); // 报告时间
                        var reportEndDate = $('input[name=reportEndDate]').val(); // 报告时间

                        var kReportStartDate = $('input[name=kReportStartDate]').val(); // 报告时间
                        if( kReportStartDate.trim().length<1 )
                        {
                            kReportStartDate = reportStartDate;
                        }
                        var kReportEndDate = $('input[name=kReportEndDate]').val(); // 报告时间
                        if( kReportEndDate.trim().length<1 )
                        {
                            kReportEndDate = reportEndDate;
                        }

                        var kUploadStartDate = $('input[name=kUploadStartDate]').val(); // 上传时间
                        var kUploadEndDate = $('input[name=kUploadEndDate]').val(); // 上传时间
                        var URL = $('input[name=URL]').val(); // URL
                        var filename = $('input[name=filename]').val(); // 文件名

                        var _url = "<?=Url::to(['export']);?>"+
                            "&reportStartDate="+reportStartDate+
                            "&reportEndDate="+reportEndDate+
                            "&kReportStartDate="+kReportStartDate+
                            "&kReportEndDate="+kReportEndDate+
                            "&URL="+URL+
                            "&filename="+filename;
                        window.location.href = _url;
                    }
                });
            });
        });
    })(jQuery);
</script>