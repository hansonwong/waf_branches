;(function ($) {  //避免全局依赖,避免第三方破坏

  $(document).ready(function () {

    var fnStatus = function (row, index, value) {
        if (parseInt(value) == 1 || parseInt(value) == 4) {
          return "<input type='button' rowid='"+index+"' class='qt bt_qyan' title='启用' />";
        } else{
          return "<input type='button' rowid='"+index+"' class='qt bt_tyan' title='停用'/>";
        }
    }
    /*调用*/
    var GridTable = $.BDGrid({
      sColumnsUrl: '../js/data/rules_title.json',
      ajax: {
        url: '../js/data/rules_list.json',
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
      width: '99.8%',
      height: '98.5%',
      pageSize: 20,
      pageSizeOptions: [10, 20, 30, 40, 50, 100],
      showRuning: false,
      //showOpen:false,//是否需要启停状态栏
      checkbox: true,
      groupColumnName: 'sTypeName',//分组名称
      groupRender: function (sTypeName){
            return '' + sTypeName + '';
      },
      // change
      columnDefs: [
          {
              targets: 'rulesName',
              data: 'rulesName',
              render: function(row, bVisible, value) {
                  var aa=$('.l-grid2 tr').eq(0).find('td').eq(2).width()-38;
                  return '<div class="rulesName" style="width'+ aa +'px">'+value+'</div>';
              }
          },
          {
              data: 'iStatus',
              targets: 'iStatus',
              render: fnStatus
          }
      ]

    });

 GridTable.on('beforerender', function (e, grid) {

    $(".g_div_table").delegate("input.qt", "click", function (e) {
          e.preventDefault();
          var  data = grid.getRow($(this).attr('rowid'));
          if($(this).hasClass('bt_qyan')){
              $(this).addClass('bt_tyan').removeClass('bt_qyan');
              $(this).attr('title','停用');
          }else{
              $(this).addClass('bt_qyan').removeClass('bt_tyan');
              $(this).attr('title','启用');
          }

         
      });
});
    // 列表操作懒启用、停用
    // $('.list_page').on('click', '.qt', function() {
    //     if($(this).hasClass('bt_qyan')){
    //         $(this).addClass('bt_tyan').removeClass('bt_qyan');
    //         $(this).attr('title','停用');
    //     }else{
    //         $(this).addClass('bt_qyan').removeClass('bt_tyan');
    //         $(this).attr('title','启用');
    //     }
    // });

    $('.list_page').delegate('input.btn_add', 'click', function () { 
      var dialog = $.Layer.iframe(
        {
          title: '添加站点组',
          url:'websitegroup_add.html',
          width: 500,
          height: 200
         
        });
    });

    GridTable.on('edit', function (e, c, table, data) {    //编辑
        e.preventDefault();
        if (data.length == 1) {
            var dialog = $.Layer.iframe({
                title: '编辑',
                url: 'websitegroup_add.html',
                width: 500,
                height: 200
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

    GridTable.on('view', function (e, c, table, data) {    //查看
        e.preventDefault();

    });

    // GridTable.on('view', function (e, c, table, data) {    //查看
    //     e.preventDefault();
    //     if (data.length == 1) {
    //         var dialog = $.Layer.iframe({
    //             title: '查看',
    //             url: 'logflow_view.html',
    //             width: 640,
    //             height: 350
    //         });
    //         dialog.hData = data[0];
    //         dialog.hGrid = table;
    //     } else {
    //         $.Layer.confirm({
    //             msg: '请选择某一行数据？', fn: function () {

    //             }
    //         });
    //     }
    // });
    //删除数据
    $('.list_page').on('click', 'input.btn_del,a.bt_del', function (e) {
      var t = $(this), r = $.grid.getSelectedRow(), l = $.Layer, g = $.grid;
      top.curd(e, t, r, l, g)
    })




  });


})(jQuery);