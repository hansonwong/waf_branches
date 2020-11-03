(function ($, window, document, undefined) {



    $.CreateTabel = function (opt) { 
        var me = this;
        var title  ='';// top.tabs && top.tabs.getCurrentTab().label;
        opt = $.extend({},  {
            alternatingRow: true,
            rownumbers: false,
            allowHideColumn:false,
            pageParmName :'start',
            pagesizeParmName :'length',
            root :'data',
            record :'Total',
            pageSize:30,
            width: '99.8%',height:'99%',
            frozenCheckbox:false,
            columnDefs:[],
            title:title
        },opt);
 

        var parentEl = opt.el || 'body', sHtml = '', title = opt.title || '';
        //sHtml = '<div class=\"seaBox\"><h1 class="title">' + title + '</h1><div class=\"other\"></div><div class=\"listBtn btn_box\"><div class="btn_list"></div></div></div>'

        $(parentEl).append('<div class="g_div_table" position="center">' + sHtml + '<div class="ligerGrid "></div></div>');
        if(opt.ajax){
            opt.url = opt.ajax.url;
            opt.parms = opt.ajax.parms;
        }
        var el = $('.ligerGrid');
        me.el = el;

       $(el).on('click', 'a.bt_edit', function () {
           var  data = me.grid.getRow($(this).attr('rowid')); 
            el.trigger('edit', [me, me.grid, [data]]);
        });
        $(el).on('click', 'a.bt_del', function () {
            var  data = me.grid.getRow($(this).attr('rowid'));
            el.trigger('del', [me, me.grid, [data]]);
        });
        $(parentEl).on('click', 'div.listBtn input.btnAdd', function () {
            el.trigger('add', [me, me.grid]);
        });
        $(parentEl).on('click', 'div.listBtn input.btnEdit', function () {
            el.trigger('edit', [me, me.grid,me.grid.getSelectedRows()]);
        });
        $(parentEl).on('click', 'div.listBtn input.btnDel', function () {
            el.trigger('del', [me, me.grid,me.grid.getSelectedRows()]);
        });

        if (opt.sColumnsUrl) {
            $.ajax({
                url: opt.sColumnsUrl,
                type: 'POST',
                dataType: 'json',
                data: {_dc: new Date()}
            }).done(function (data) {

                if(opt.columnDefs){
                    opt.columnDefs.forEach(function(item){
                        data.forEach(
                            function(v,i){
                                if(v.sClass == item.targets){
                                    data[i].render = item.render;

                                }
                            }
                        )

                    });

                }
                data.forEach(
                    function(v,i){

                        if(v.sClass == 'btn_del'){
                            /* $('<input type=\"button\" class=\"btn btnDel btn_del\" value="删除">').appendTo('div.btn_list'); */
                            $('<input type=\"button\" class=\"btn btnDel btn_del\" value="'+baseLanguage.common.deletes+'">').appendTo('div.btn_list');
                            opt.checkbox = true;
                            opt.del = true;
                        };
                        if(v.sClass == 'btn_edit'){
                            /* $('<input type=\"button\" class=\"btn btnAdd btn_add\" value="增加">').appendTo('div.btn_list');
                            $('<input type=\"button\" class=\"btn btnEdit btn_edit\" value="编辑">').appendTo('div.btn_list'); */
                            $('<input type=\"button\" class=\"btn btnAdd btn_add\" value="'+baseLanguage.common.pushAdd+'">').appendTo('div.btn_list');
                            $('<input type=\"button\" class=\"btn btnEdit btn_edit\" value="'+baseLanguage.common.website_edit+'">').appendTo('div.btn_list');
                            opt.checkbox = false;
                            opt.edit = true;
                        };
                        if( data[i].bVisible !=  false){
                        }else{
                            data[i].hide = true;
                            data[i].width = -1;
                        }
                        if(  data[i].data){
                            data[i].name =   data[i].data;
                        }
                        if(  data[i].sTitle){
                            data[i].display =   data[i].sTitle;
                        }
                    }
                )
                data.unshift({
                    // name: 'id', display: '操作',width:100,  isAllowHide: false,
                    name: 'id', display: baseLanguage.common.options,width:100,  isAllowHide: false,
                    // name: 'id', display: '操作3',width:100,  isAllowHide: false,
                    render: function (record, rowindex, value, column) {
                        var html = [] ;
                        if( opt.edit == true){
                            html.push( "<a href='javascript:;' class='bt_edit'    rowid='"+rowindex+"'>&nbsp;&nbsp; &nbsp;&nbsp;</a>");
                        }
                        if( opt.del == true){
                            html.push( "<a  href='javascript:;' class='bt_del'  rowid='"+rowindex+"'>&nbsp;&nbsp;&nbsp;&nbsp;</a>");
                        }
                        return html.join('&nbsp;&nbsp;');
                    }
                });
                opt.columns = data;
                var d =   $('.ligerGrid').ligerGrid(opt);
                me.grid = d;
                me.el.trigger('beforerender',[d]);
            }).fail(function () {
            });
        }else{ 
			    var d =   $('.ligerGrid').ligerGrid(opt);
                me.grid = d;
                me.el.trigger('beforerender',[d]);
		}
        return   me.el;

    }

})(jQuery, window, document);


