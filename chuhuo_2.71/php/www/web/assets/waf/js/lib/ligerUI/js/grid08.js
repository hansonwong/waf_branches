
;(function($){  //避免全局依赖,避免第三方破坏
	
    $(document).ready(function () {
        /*调用*/
		var GridTable = $.BDGrid({
            sColumnsUrl: '../js/data/GetHeaderTitle.json',
            ajax: {
                url: '../js/data/IndexListData1.json',
                type: 'POST'
            },
			el:'#maingrid',
			dataAction:'local',
			showSitting:false,//是否需要操作列
			showEdit:false,
			showView:true,
			showDel:true,
			showLock:false,//是否需要解锁和锁定状态栏
			isSelectR:true,//复选按钮是否选中
			width: '99.8%',
			height:'99%',
			pageSize: 20, 
			pageSizeOptions: [10, 20, 30, 40, 50, 100],
			checkbox: true
        });
		$('.list_page').delegate('input.btn_add', 'click', function () { 
			var dialog = $.Layer.iframe(
				{
					title: '新增FTP共享服务器',
					url:'add_rep.html',
					width: 500,
					height: 420
				});
		});
        GridTable.on('view', function (e, c, table, data) {    //查看FTP共享服务器
            e.preventDefault();
            if (data.length == 1) {
                var dialog = $.Layer.iframe({
                    title: '查看FTP共享服务器',
                    url: 'add_rep.html',
                    width: 500,
                    height: 420,
                    button:false,
                    cancel:null
                });
                dialog.hData = data[0];
                dialog.hGrid = table;
            } else {
                $.Layer.confirm({
                    msg: '请选择某一行数据？', fn: function () {

                    }
                });
            }
        });
		//删除FTP共享服务器
      $('.list_page').on('click', 'input.btn_del,a.bt_del', function (e) {
        var t = $(this), r = $.grid.getSelectedRow(), l = $.Layer, g = $.grid;
        top.curd(e, t, r, l, g)
      })


      $(".l-grid-row:odd").css("background-color","#f9f9f9");//列表间隔行
		
    });
})(jQuery);