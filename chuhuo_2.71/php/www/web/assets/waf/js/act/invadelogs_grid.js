;(function ($) {  //避免全局依赖,避免第三方破坏

  $(document).ready(function () {
    /*调用*/
    var GridTable = $.BDGrid({
      sColumnsUrl: '../js/data/invadelogs_title.json',
      ajax: {
        url: '../js/data/invadelogs_list.json',
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
      width: '99.8%',
      height: '98.5%',
      pageSize: 20,
      pageSizeOptions: [10, 20, 30, 40, 50, 100],
      showRuning: false,
      checkbox: true,
      detail: {
        height: 'auto', onShowDetail: function (r, p) {
          $(p).append($('<table cellpadding="0" cellspacing="0" style="width:95%;" class="detailtd"><tr><td align="right" class="dtd" width="120">规则模块：</td><td>' + r.ruleMode + '</td></tr><tr><td align="right" class="dtd">规则名称：</td><td>' + r.ruleName + '</td></tr><tr><td align="right" class="dtd">一般信息：</td><td>' + r.messages + '</td></tr><tr><td align="right" class="dtd">匹配内容：</td><td>' + r.matcheddata + '</td></tr><tr><td align="right" class="dtd">规则ID：</td><td>' + r.ruleId + '</td></tr></table>').css('margin', '20px auto'));

        }
      }
    });

    //删除数据

    $('.list_page').on('click', 'input.btn_del,a.bt_del', function (e) {
      var t = $(this), r = $.grid.getSelectedRow(), l = $.Layer, g = $.grid;
      top.curd(e, t, r, l, g)
    })


    $('.list_page').delegate('.btn_clear', 'click', function () { 
        $.Layer.confirm({
          title: '系统友情提示', msg:'<span class="red">'+'清空操作将对目前查询条件所列数据进行清空，清空后将不能恢复,确认?'+'</span>', fn: function () {

          }
        });
    }); 

    $('.list_page').delegate('.btn_exp', 'click', function () { 
        $.Layer.confirm({
          title: '系统友情提示', msg:'提示:  将根据当前条件导出日志,最多导出最新的50000条记录.', fn: function () {

          }
        });
    }); 


  });
})(jQuery);