;(function ($) {  //避免全局依赖,避免第三方破坏

  $(document).ready(function () {
    /*调用*/
    var GridTable = $.BDGrid({
      sColumnsUrl: '../js/data/GetHeaderTitle2.json',
      ajax: {
        url: '../js/data/IndexListData2.json',
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
      showUseed: true,
      width: '99.8%',
      height: '99%',
      pageSize: 20,
      pageSizeOptions: [10, 20, 30, 40, 50, 100],
      checkbox: true
    });

    $('.list_page').delegate('input.btn_add', 'click', function () {
      var dialog = $.Layer.iframe(
        {
          title: '添加备份策略',
          url: 'add_tjbf.html',
          width: 540,
          height: 410
        });
    });
    GridTable.on('edit', function (e, c, table, data) {    //编辑备份策略
      e.preventDefault();
      if (data.length == 1) {
        var dialog = $.Layer.iframe({
          title: '编辑备份策略',
          url: 'add_tjbf.html',
          width: 540,
          height: 410
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
    GridTable.on('view', function (e, c, table, data) {    //查看备份策略
      e.preventDefault();
      if (data.length == 1) {
        var dialog = $.Layer.iframe({
          title: '查看备份策略',
          url: 'add_tjbf.html',
          width: 540,
          height: 410
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
    $('.list_page').on('click', 'input.btn_del,a.bt_del', function (e) {
      var t = $(this), r = $.grid.getSelectedRow(), l = $.Layer, g = $.grid;
      top.curd(e, t, r, l, g)
    })

    $(".l-grid-row:odd").css("background-color", "#f9f9f9");//列表间隔行
    $(".l-grid-row input").removeClass("qt");
  });
})(jQuery);