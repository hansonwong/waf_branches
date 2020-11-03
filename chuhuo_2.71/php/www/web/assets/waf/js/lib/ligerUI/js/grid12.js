
;(function($){  //避免全局依赖,避免第三方破坏
	
    $(document).ready(function () {
        /*调用*/
		var GridTable = $.BDGrid({
            sColumnsUrl: '../js/data/testHeaderTitle1.json',
            ajax: {
                url: '../js/data/testListData1.json',
                type: 'POST'
            },
			el:'#maingrid',
			dataAction:'local',
			showSitting:false,//是否需要操作列
			showEdit:false,
			showView:false,
			showDel:false,
			showLock:false,//是否需要解锁和锁定状态栏
			isSelectR:false,//复选按钮是否选中
			width: '99.8%',
			height:'98.5%',
			pageSize: 20, 
			pageSizeOptions: [10, 20, 30, 40, 50, 100],
			showRuning:false,
			checkbox: false,
			TableISelect:false,
			detail: { onShowDetail: f_showOrder },
			onError: function (a, b)
                { 
                }
        });

		$(".l-grid-row:odd").css("background-color","#f9f9f9");//列表间隔行
		
    });
	
	
	function f_showOrder(row, detailPanel,callback)
        {
            var grid = '<div id="maingrid1" style="margin:15px;margin-bottom:0;"></div>'; 
            $(detailPanel).append(grid);
            var GridTable1 = $.BDGrid({
				sColumnsUrl: '../js/data/testHeaderTitle2.json',
				ajax: {
					url: '../js/data/testListData2.json',
					type: 'POST'
				},
				el:'#maingrid1',
				dataAction:'local',
				showSitting:false,//是否需要操作列
				showEdit:false,
				showView:false,
				showDel:false,
				showLock:false,//是否需要解锁和锁定状态栏
				isSelectR:false,//复选按钮是否选中
				width: '99.8%',
				height:260,
				pageSize: 5, 
				pageSizeOptions: [5,10, 20, 30, 40, 50, 100],
				showRuning:false,
				checkbox: false,
				TableISelect:false,
			});  
        }
	
	
})(jQuery);