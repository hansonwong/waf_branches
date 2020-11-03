;(function ($) {  //避免全局依赖,避免第三方破坏

  $(document).ready(function () {
    /*调用*/
    var GridTable = $.BDGrid({
      sColumnsUrl: '../js/data/custom_title.json',
      ajax: {
        url: '../js/data/custom_list.json',
        type: 'POST'
      },
      el: '#maingrid',
      dataAction: 'local',
      showSitting: false,//是否需要操作列
      showEdit: true,
      showView: false,
      showDel: true,
      showLock: false,//是否需要解锁和锁定状态栏
      isSelectR: true,//复选按钮是否选中
      width: '99.8%',
      height: '98.5%',
      pageSize: 20,
      pageSizeOptions: [10, 20, 30, 40, 50, 100],
      showRuning: false,
      showOpen:true,//是否需要启停状态栏
      checkbox: true
    });

    // 列表操作懒启用、停用
    $('.list_page').on('click', '.qt', function(event) {
        if($(this).hasClass('bt_qyan')){
            $(this).addClass('bt_tyan').removeClass('bt_qyan');
            $(this).attr('title','停用');
        }else{
            $(this).addClass('bt_qyan').removeClass('bt_tyan');
            $(this).attr('title','启用');
        }
    });

    $('.list_page').delegate('input.btn_add', 'click', function () { 
      var dialog = $.Layer.iframe(
        {
          title: '添加自定义规则',
          url:'custom_add.html',
          width: 500,
          height: 600
         
        });
    });

    GridTable.on('edit', function (e, c, table, data) {    //编辑
        e.preventDefault();
        if (data.length == 1) {
            var dialog = $.Layer.iframe({
                title: '编辑',
                url: 'custom_add.html',
                width: 500,
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