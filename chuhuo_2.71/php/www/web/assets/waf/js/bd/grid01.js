
;(function($){  //避免全局依赖,避免第三方破坏
	
    $(document).ready(function () {
        /*调用*/
		var GridTable = $.BDGrid({
            sColumnsUrl: '../../js/data/GetHeaderTitle.json',
            ajax: {
                url: '../../js/data/IndexListData.json',
                type: 'POST'
            },
			el:'.grid',
			dataAction:'local',
			showSitting:true,//是否需要操作列
			showLock:true,//是否需要解锁和锁定状态栏
			isSelectR:true,//复选按钮是否选中
			width: '99.8%',
			height:'220',
			checkbox: true
        });
		GridTable.on('add', function (e, c, table) {   //增加实验机架
            e.preventDefault();
            var dialog = $.Layer.iframe(
                {
                    title: '增加实验机架',
                    url:'grid/Save.html',
                    width: 460,
                    height: 140
                });
            dialog.hGrid = table;
			//console.log(table.data);
        });
        GridTable.on('edit', function (e, c, table, data) {    //编辑实验机架
            e.preventDefault();
            if (data.length == 1) {
                var dialog = $.Layer.iframe({
                    title: '编辑实验机架',
                    url: 'grid/Save.html',
                    width: 460,
                    height: 140
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
		GridTable.on('view', function (e, c, table, data) {    //查看实验机架
            e.preventDefault();
            if (data.length == 1) {
                var dialog = $.Layer.iframe({
                    title: '查看实验机架',
                    url: 'grid/Save.html',
                    width: 460,
                    height: 140
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
		//删除实验机架
		$('.list_page').on('click', 'input.btn_del,a.bt_del', function (e) {
	      var t = $(this), r = $.grid.getSelectedRow(), l = $.Layer, g = $.grid;
	      top.curd(e, t, r, l, g)
	    })

		$(".l-grid-row:odd").css("background-color","#f9f9f9");//列表间隔行
		
    });
})(jQuery);