;(function ($) {  //避免全局依赖,避免第三方破坏

  $(document).ready(function () {
    /*调用*/
    var GridTable = $.BDGrid({
      sColumnsUrl: '../js/data/outlink_title.json',
      ajax: {
        url: '../js/data/outlink_list.json',
        type: 'POST'
      },
      el: '#maingrid',
      dataAction: 'local',
      showSitting: false,//是否需要操作列
      showEdit: false,
      showView: false,
      showDel: false,
      showLock: false,//是否需要解锁和锁定状态栏
      isSelectR: true,//复选按钮是否选中
      showOpen:false,//是否需要启停状态栏
      showSetting:true, //是否显示配置按钮      
      width: '99.8%',
      height: '98.5%',
      pageSize: 20,
      pageSizeOptions: [10, 20, 30, 40, 50, 100],
      showRuning: false,
      checkbox: true,
      columnDefs: [
          {
              targets: 'zxdz',
              data: 'zxdz',
              render: function (row, bVisible, value){
                if(value == 0){
                    var str = '<font class="red">拦截</font>';
                }else if(value == 1) {
                    var str = '<font class="green">放行</font>';
                }
                return str;                             
              }
          }
      ]      
    });



    //删除数据
    $('.list_page').on('click', 'input.btn_del,a.bt_del', function (e) {
      var t = $(this), r = $.grid.getSelectedRow(), l = $.Layer, g = $.grid;
      top.curd(e, t, r, l, g)
    })




  });
})(jQuery);