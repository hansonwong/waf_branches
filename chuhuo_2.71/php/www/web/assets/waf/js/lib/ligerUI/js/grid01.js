;(function ($) {  //避免全局依赖,避免第三方破坏

  $(document).ready(function () {
    /*调用*/
    var GridTable = $.BDGrid({
      sColumnsUrl: '../js/data/GetHeaderTitle.json',
      ajax: {
        url: '../js/data/IndexListData11.json',//报表链接错误，或者无数据时，显示无数据图标 change by Siven.
        type: 'POST'
      },
      el: '#maingrid',
      dataAction: 'local',
      showSitting: false,//是否需要操作列
      showEdit: false,
      showView: true,
      enabledSort: true,  //表格排序功能开启 change by Siven.
      showDel: false,
      showLock: false,//是否需要解锁和锁定状态栏
      isSelectR: true,//复选按钮是否选中
      width: '99.8%',
      height: '99%',
      pageSize: 20,
      pageSizeOptions: [10, 20, 30, 40, 50, 100],
      checkbox: true
    });
    GridTable.on('add', function (e, c, table) {   //增加实验机架
      e.preventDefault();
      var dialog = $.Layer.iframe(
        {
          title: '增加实验机架',
          url: 'save.html',
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
          url: 'save.html',
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
          url: 'save.html',
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
    // GridTable.setColumnWidth('',20)
    //删除实验机架

    $('.list_page').on('click', 'input.btn_del,a.bt_del', function (e) {
      var t = $(this), r = $.grid.getSelectedRow(), l = $.Layer, g = $.grid;
      top.curd(e, t, r, l, g)
    })


    $(".l-grid-row:odd").css("background-color", "#f9f9f9");//列表间隔行

  });
})(jQuery);