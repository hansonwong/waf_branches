;(function ($) {  //避免全局依赖,避免第三方破坏

  $(document).ready(function () {
    /*调用*/
    var GridTable = $.BDGrid({
      sColumnsUrl: '../js/data/website_title_zd.json',
      ajax: {
        url: '../js/data/website_list_zd.json',
        type: 'POST'
      },
      el: '#maingrid',
      dataAction: 'local',
      showSitting: false,//是否需要操作列
      showEdit: true,
      showView: true,
      showDel: true,
      showLock: false,//是否需要解锁和锁定状态栏
      isSelectR: true,//复选按钮是否选中
      showSetting:true, //是否显示配置按钮
      width: '99.8%',
      height: '99.8%',
      pageSize: 20,
      pageSizeOptions: [10, 20, 30, 40, 50, 100],
      showRuning: false,
      checkbox: true
    });

    $('.list_page').delegate('input.btn_add', 'click', function () { 
      var dialog = $.Layer.iframe(
        {
          title: '添加站点',
          url:'website_zd_add.html',
          width: 650,
          height: 250
         
        });
    });

    GridTable.on('edit', function (e, c, table, data) {    //编辑
        e.preventDefault();
        if (data.length == 1) {
            var dialog = $.Layer.iframe({
                title: '修改站点',
                url: 'website_zd_add.html',
                width: 650,
                height: 250
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


    //删除数据
    $('.list_page').on('click', 'input.btn_del,a.bt_del', function (e) {
      var t = $(this), r = $.grid.getSelectedRow(), l = $.Layer, g = $.grid;
      top.curd(e, t, r, l, g)
    })

    GridTable.on('setting',  function (e, c, table, data) { 
      e.preventDefault();
        if (data.length == 1) {
          var dialog = $.Layer.iframe({
              title: '配置策略',
              url:'website_zd_setting.html',
              width: 450,
              height: 250
             
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

  });
})(jQuery);