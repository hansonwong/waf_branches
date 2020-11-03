
;(function($){  //避免全局依赖,避免第三方破坏
	
    $(document).ready(function () {
        /*调用*/
		var GridTable = $.BDGrid({
            sColumnsUrl: '../js/data/testHeaderTitle2.json',
            ajax: {
                url: '../js/data/testListData2.json',
                type: 'POST'
            },
			el:'#maingrid',
			dataAction:'local',
			showSitting:false,//是否需要操作列
			showEdit:false,
			showView:true,
			showDel:false,
			showLock:false,//是否需要解锁和锁定状态栏
			isSelectR:true,//复选按钮是否选中
			width: '99.8%',
			height:'98.5%',
			pageSize: 20, 
			pageSizeOptions: [10, 20, 30, 40, 50, 100],
			showRuning:true,
			showComputer:true,
			checkbox: true
        });
		
		//删除数据

      $('.list_page').on('click', 'input.btn_del,a.bt_del', function (e) {
        var t = $(this), r = $.grid.getSelectedRow(), l = $.Layer, g = $.grid;
        top.curd(e, t, r, l, g)
      })


		$(".l-grid-row:odd").css("background-color","#f9f9f9");//列表间隔行
		
    });
})(jQuery);