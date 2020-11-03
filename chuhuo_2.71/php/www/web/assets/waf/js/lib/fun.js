/**
 * Created by Administrator on 2017/3/20.
 */
$(function(){
  window.curd = function(e,t,r,l,g){
    //e 事件
    //t 当前this
    //r 选择的行
    //l 弹框
    //g gird对象
    e.preventDefault();
    var $this = t;
    var row = r;
    if (!row && $this[0].tagName == 'INPUT') {
      l.confirm({
        msg: '请选择数据？', fn: function () {
        }
      });
      return;
    } else if (row && $this[0].tagName != 'A') {
      l.confirm({
        msg: '是否要删除数据？', fn: function () {
          g.deleteSelectedRow();
        }
      });
    }
    if ($this[0].tagName == 'A') {
      var rowid = $this.attr('rowid');
      l.alert({
        msg: 'alert bug 展示，不删除数据'
      })
      // l.confirm({
      //   msg: '是否要删除数据？', fn: function () {
      //     g.deleteRow(rowid);
      //     console.log(g.deleteRow(rowid))
      //   }
      // });
    }
  }
})