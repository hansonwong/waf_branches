
;(function($){  //避免全局依赖,避免第三方破坏
	
    $(document).ready(function () {
        /*调用*/
		var GridTable = $.BDGrid({
            sColumnsUrl: '../js/data/GetHeaderTitle1.json',
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
			showLock:true,//是否需要解锁和锁定状态栏
			isSelectR:true,//复选按钮是否选中
			width: '99.8%',
			height:'99%',
			pageSize: 20, 
			pageSizeOptions: [10, 20, 30, 40, 50, 100],
			checkbox: true,
			detail: {height:'auto', onShowDetail: function (r, p){ 
                    $(p).append($('<table cellpadding="0" cellspacing="0" style="width:95%;" class="detailtd"><tr><td align="right" class="dtd">姓名：</td><td>' + r.sFrameName + '</td><td align="right" class="dtd">部门名称：</td><td>' + r.sFrameDesc + '</td></tr><tr><td align="right" class="dtd">IP地址：</td><td>' + r.sFrameType + '</td><td align="right" class="dtd">MAC地址：</td><td>' + r.sFrameMAC + '</td></tr><tr><td align="right" class="dtd">国籍：</td><td>' + r.sFrameCount + '</td><td align="right" class="dtd">证件类型：</td><td>' + r.sFrameCARD + '</td></tr><tr><td align="right" class="dtd" >上网许可：</td><td colspan="3">' + r.sFrameNET + '</td></tr></table>').css('margin', '20px auto'));

                }
           }
        });

		$('.list_page').delegate('input.btn_add', 'click', function () { 
			var dialog = $.Layer.iframe(
				{
					title: '新增管理员',
					url:'add_admin.html',
					width: 500,
					height: 420
			   
				});
		});
        GridTable.on('edit', function (e, c, table, data) {    //编辑管理员
            e.preventDefault();
            if (data.length == 1) {
                var dialog = $.Layer.iframe({
                    title: '编辑管理员',
                    url: 'add_admin.html',
                    width: 500,
                    height: 420
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
		GridTable.on('view', function (e, c, table, data) {    //查看管理员信息
            e.preventDefault();
            if (data.length == 1) {
                var dialog = $.Layer.iframe({
                    title: '查看管理员信息',
                    url: 'add_admin.html',
                    width: 500,
                    height: 420
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

        // 启用、停用
        $('.list_page').on('click', '.qt', function(event) {
            if($(this).hasClass('bt_qyan')){
                $(this).addClass('bt_tyan').removeClass('bt_qyan');
            }else{
                $(this).addClass('bt_qyan').removeClass('bt_tyan');
            }
        });
		
		//删除用户姓名
      $('.list_page').on('click', 'input.btn_del,a.bt_del', function (e) {
        var t = $(this), r = $.grid.getSelectedRow(), l = $.Layer, g = $.grid;
        top.curd(e, t, r, l, g)
      })




    });
})(jQuery);