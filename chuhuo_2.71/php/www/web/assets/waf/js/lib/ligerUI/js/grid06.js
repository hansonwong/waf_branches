
;(function($){  //避免全局依赖,避免第三方破坏
	
    $(document).ready(function () {
        /*调用*/
		var GridTable = $.BDGrid({
            sColumnsUrl: '../js/data/testHeaderTitle3.json',
            ajax: {
                url: '../js/data/testListData3.json',
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
			showNumb:true,
			checkbox: true,
			detail: {height:'auto', onShowDetail: function (r, p)
                { 
                    $(p).append($('<table cellpadding="0" cellspacing="0" style="width:95%;" class="detailtd"><tr><td align="right" class="dtd">设备编号：</td><td>' + r.sFrameName + '</td><td align="right" class="dtd">位置：</td><td>' + r.sFrameDesc + '</td></tr><tr><td align="right" class="dtd">厂家编号：</td><td>' + r.sFrameType + '</td><td align="right" class="dtd">设备类型：</td><td>' + r.sFrameCPU + '</td></tr><tr><td align="right" class="dtd">通信IP：</td><td>' + r.sFrameCP + '</td><td align="right" class="dtd">通信MAC：</td><td>' + r.sFrameJx + '</td></tr><tr><td align="right" class="dtd">通信掩码：</td><td>' + r.sFrameLl + '</td><td align="right" class="dtd">通信网关：</td><td>' + r.sFrameZj + '</td></tr><tr><td align="right" class="dtd">管理口IP：</td><td>' + r.sFrameZj + '</td><td align="right" class="dtd">管理口MAC：</td><td>' + r.sFrameZj + '</td></tr><tr><td align="right" class="dtd">管理口掩码：</td><td>' + r.sFrameZj + '</td><td align="right" class="dtd">管理口网关：</td><td>' + r.sFrameZj + '</td></tr><tr><td align="right" class="dtd">中心地址：</td><td>' + r.sFrameZj + '</td><td align="right" class="dtd">副中心地址：</td><td>' + r.sFrameJx + '</td></tr><tr><td align="right" class="dtd">产品版本号：</td><td>' + r.sFrameZj + '</td><td align="right" class="dtd">DNS策略版本号：</td><td>' + r.sFrameJx + '</td></tr><tr><td align="right" class="dtd">IP策略版本号：</td><td>' + r.sFrameZj + '</td><td align="right" class="dtd">IP地理库版本号：</td><td>' + r.sFrameJx + '</td></tr><tr><td align="right" class="dtd">涉密标识版本号：</td><td>' + r.sFrameZj + '</td><td align="right" class="dtd">木马规则版本号：</td><td>' + r.sFrameJx + '</td></tr><tr><td align="right" class="dtd">邮件策略版本号：</td><td>' + r.sFrameZj + '</td><td align="right" class="dtd">私有策略版本号：</td><td>' + r.sFrameJx + '</td></tr></table>').css('margin', '20px auto'));

                }
                }
        });
		
		//删除数据

      $('.list_page').on('click', 'input.btn_del,a.bt_del', function (e) {
        var t = $(this), r = $.grid.getSelectedRow(), l = $.Layer, g = $.grid;
        top.curd(e, t, r, l, g)
      })


		$(".l-grid-row:odd").css("background-color","#f9f9f9");//列表间隔行
		
    });
})(jQuery);