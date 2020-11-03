;(function ($) {  //避免全局依赖,避免第三方破坏

  $(document).ready(function () {
    /*调用*/
    var GridTable = $.BDGrid({
      sColumnsUrl: '../js/data/flaw_title.json',
      ajax: {
        url: '../js/data/flaw_list.json',
        type: 'POST'
      },
      el: '#maingrid',
      dataAction: 'local',
      showSitting: false,//是否需要操作列
      showEdit: false,
      showView: true,
      showDel: false,
      showLock: false,//是否需要解锁和锁定状态栏
      isSelectR: true,//复选按钮是否选中
      showScan:true, //是否显示扫描按钮
      showDownload:true, //是否显示下载按钮
      showStop:true, //是否显示启动停止按钮
      showQidong:true, //是否显示启动按钮
      width: '99.8%',
      height: '99.8%',
      pageSize: 20,
      pageSizeOptions: [10, 20, 30, 40, 50, 100],
      showRuning: false,
      //showScanStatus:true,//是否显示扫描状态
      checkbox: true,
      columnDefs: [
          {
              targets: 'smzt',
              data: 'smzt',
              render: function (row, bVisible, value){
                if (value == 1){
                  var str = "<font class='green'>扫描中</font>";
                } else if (value == 2){
                  var str = "<font class='gray'>已完成</font>";
                } else if (value == 3){
                  var str = "<font class='red'>已停止</font>";
                }  
                return str;                             
              }
          }
      ]       
    });


    $('.list_page').delegate('input.btn_add', 'click', function () { 
      var dialog = $.Layer.iframe(
        {
          title: '添加',
          url:'flaw_add.html',
          width: 500,
          height: 250
         
        });
    });

    GridTable.on('view', function (e, c, table, data) {    //查看
        e.preventDefault();
        if (data.length == 1) {
            var dialog = $.Layer.iframe({
                title: '查看',
                url: 'flaw_view.html',
                width: 950,
                height: 600
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


  });
})(jQuery);