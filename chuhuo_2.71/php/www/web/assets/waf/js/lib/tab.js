
    var tabs = {},tabsId=[];
    $(document).ready(function () {

        $('.font-weight td a').click(function(){
            if (!$(this).attr("link")) {
                return false;
            } else {

                parent.addTab({//调用addTab函数，传title和url的参数
                    title: $(this).text(),

                    url: $(this).attr('link')
                });

            }
        });

        $('.m_title a').click(function(){

            if (!$(this).attr("link")) {
                return false;
            } else {

                parent.addTab({//调用addTab函数，传title和url的参数
                    title: $(this).text(),

                    url: $(this).attr('link')
                });

            }
        });


        $('#tabs').delegate('a.tab', 'click', function (e) {
            // 隐藏所有tab和iframe
            $("#tabs li").removeClass("current");
            $("#content iframe").hide();

            // 显示点击的tab及iframe
            $(this).parent().addClass("current");
            var contentname = $(this).attr("id") + "_content";
            $("#" + contentname).show();


        });
        $('#tabs').delegate('a.remove', 'click', function (e) {
            var me = e.currentTarget,wl=0;
            var id = $(me).attr('pid');
            var src = $("#" + id + "_content").attr('src');
            var wd_box = $(".l-tab-links").width();
            delete tabs[src];
            var cur = $('#' + id).parent().prev();
            $('#' + id).parent().remove();

            if ($("#tabs li.current").length == 0 && $("#tabs li").length > 0) {
                cur.addClass("current");
                var hid = cur.find('a.tab').attr('id');
                $("#" + hid + "_content").show();
            };
            //luoxiaohong
            $("#tabs li").each(function(index, element) {
                wl += $(this).outerWidth(true);
            });

            if(wl<=wd_box){
                $(".sc-bt,.l-tab-links-close").remove();
                $("#tabs").css({left:"4px"});
            }else{
                $("#tabs").css({left:-wl+wd_box-20});
            }
        });

        addTab({
            title: welcomePageTitle,
            close: false,
            url: welcomePageUrl
        });
    });

    $(window).resize(function(){
        addScroll();
    });
     function selectTab(obj){
        if(obj == 1){
             $('.menu').delegate('li a', 'click', function () {
        
                if (!$(this).attr("link")) {
                    return false;
                } else {
    
                    addTab({//调用addTab函数，传title和url的参数
                        title: $(this).text(),
    
                        url: $(this).attr('link')
                    });
                }
               //luoxiaohong
                addScroll();
            });

        }
        
        if(obj == 2){
                //显示TAB的菜单点击事件
                $('#documents li a.select').on('contextmenu',function(e){
                    $(".selectChange").remove();
                    var url = $(this).attr("link");
                    var rel = $(this).attr("rel");
                    var innerHtml = $(this).children("p").text();
                    var html = '<a link="'+url+'" rel="'+rel+'" target="right" class="selectChange">TAB显示</a>';
                    $(this).parent("li").append(html);
                    $(".selectChange").attr("title",innerHtml);
                    e.preventDefault();
                    $(".selectChange").click(function(){
                        $(this).hide(); 
                        $("#documents li a").removeClass("sel");
                        $("#documents li a").children("p").removeClass("aselec");
                        $(".l-tab-links").show().siblings(".t-tab-links").hide();
                        $(this).siblings("a").addClass("sel").children("p").addClass("aselec");;
                    });
                });
                $("#documents li").hover(function(){
                    $(this).siblings().children(".selectChange").remove();
                });
                //返回系统主页的iframe调用
                $(".t-tab-links").delegate('a', 'click',function(){
                    var url = $(this).attr("link");
                    $(".iframeclass").attr("src",url);
                    $(this).siblings("span").hide();
                });
                //没有TAB的菜单点击事件
                $('a.select').on('click',  function () {
                    $("#content iframe.iframeclass").remove();
                    $("#content iframe").hide();
                    var url = $(this).attr("link");
                    var html = $(this).children("p").text();
                    $("#content").append("<iframe name='right' class='iframeclass' frameborder='0' src='" + url + "'  scrolling='auto' ></iframe>");
                    $(".t-tab-links").children("span").show();
                    $(".t-tab-links").children().children("b").html(html)
                    $(".t-tab-links").show().siblings(".l-tab-links").hide();
                });
                //TAB的关闭点击事件
                $("a.l-tab-links-close").on('click', function (){
                    var text = $("#tabs li.current").children("a.tab").text();
                    var menuli = $("#documents").find("li");
                    $(".l-tab-links").hide();
                    $(".t-tab-links").show();
                    
                    for(var i=0;i<menuli.length;i++){
                        var menulist =$(menuli[i]);
                        var ptext = menulist.children().children("p").text();
                        //console.log(ptext);
                        if(ptext===text){
                            menuli.children("a").removeClass("sel");
                            menuli.children("a").children("p").removeClass("aselec");
                            menulist.children("a").addClass("sel");
                            menulist.children("a").children("p").removeClass("aselec");
                            $(".t-tab-links").children("span").show();
                            $(".t-tab-links").children("span").children("b").html(text);
                        }
                    }
                    
                });
                 $('.menu').delegate('li a.selectChange', 'click',  function () {
                    $(".iframeclass").remove();
                    if (!$(this).attr("link")) {
                        return false;
                    } else {
        
                        addTab({//调用addTab函数，传title和url的参数
                            title: $(this).attr("title"),
        
                            url: $(this).attr('link')
                        });
                    }
                   addScroll();
        
                });
            }
        
    }
    function addScroll(){
        var _tab = $("#tabs"),
            _tabDiv = _tab.parent(".l-tab-links");
            _tabLi = _tab.children("li"),
            _wAll=0,
            _tabWidth = _tabDiv.width();
            $(".sc-bt").remove();$(".l-tab-links-close").remove();
            _tabLi.each(function(index, element) {
                _wAll += $(this).outerWidth(true);
            });
         if(_wAll>_tabWidth){
             var wd = _wAll-_tabWidth-27;
             _tabDiv.append('<a class="sc-bt scrollLeft" href="javascript:;"></a><a class="sc-bt scrollRight" href="javascript:;"></a>');
             _tab.css("left",-wd);
             var tabItems = _tab.children("li");
             //左滚动按钮
            $(".scrollLeft").click(function(){
                var bd = $(this);
                var prevBtnOffset = bd.offset();
                var prevBtnLeft = prevBtnOffset.left + bd.outerWidth();
                var left;
                var tableft = parseInt(_tab.css("left"));
                var mgleft = parseInt(tabItems.css("margin-left"));
                for (var i=0;i<tabItems.length;i++){
                     var tabitem = $(tabItems[i]);
                     var offset = tabitem.offset();
                     var start = offset.left, end = offset.left + tabitem.outerWidth();
                     if(start < prevBtnLeft && end >= prevBtnLeft){
                        left = tableft + prevBtnLeft - start + mgleft;
                        $("#tabs").animate({left: left },500);
                        //console.log(tableft,prevBtnLeft,start,mgleft,bd.outerWidth(),left);
                     }
                     
                }
                
                return true;
            });
            //右滚动按钮
            $(".scrollRight").click(function(){
                var bdr = $(this);
                var prevBtnOffset = bdr.offset();
                var prevBtnLeft = prevBtnOffset.left;
                var left;
                var tableft = parseInt(_tab.css("left"));
                var mgleft = parseInt(tabItems.css("margin-left"));
                for (var i=0;i<tabItems.length;i++){
                     var tabitem = $(tabItems[i]);
                     var offset = tabitem.offset();
                     var start = offset.left, end = offset.left + tabitem.outerWidth();
                     if(start <= prevBtnLeft && end > prevBtnLeft){
                        left = tableft - (end - prevBtnLeft + mgleft+1) ;
                        //console.log(tableft,prevBtnLeft,start,mgleft,bdr.outerWidth(),left);
                        $("#tabs").animate({left: left },500);
                     }
                     
                }
                return true;
            });
            
          }else{
              _tab.css("left",0);
              $(".sc-bt").remove();
          }
          
        
    };

    function addTab(obj) {
        // hide other tabs

        // var iframeId = tabs[obj.url];
        // if (iframeId) {
        //     $("#tabs li").removeClass("current");
        //     $("#content iframe").hide();
        //     $("#" + iframeId).parent().addClass("current");
        //     // 强制刷新当前iframe --Siven
        //     $("#" + iframeId+'_content')[0].src = $("#" + iframeId+'_content')[0].src
        //     $("#" + iframeId+'_content').show();
        //     return
        // }
        // tab最多显示7个 change by linfang 2017/11/29
        var iframeId = tabs[obj.url];
        if (iframeId) {
            $("#tabs li").removeClass("current");
            $("#content iframe").hide();
            $("#" + iframeId).parent().addClass("current");
            // 强制刷新当前iframe --Siven
            //$("#" + iframeId+'_content')[0].src = $("#" + iframeId+'_content')[0].src
            $("#" + iframeId+'_content').show();
            return
        }        
        var tabs_num = $("#tabs li").length;
        if (tabs_num > 7) {
          //清掉第二个tab
            var sendTab = tabsId.splice(1,1);
           var id = sendTab[0];
            var src = $("#" + id + "_content").attr('src');
            delete tabs[src];
            var cur = $('#' + id).parent().prev();
            $('#' + id).parent().remove();
        }

        $("#tabs li").removeClass("current");
        $("#content iframe").hide();

            var tick = new Date().getTime(), close = '';
            obj.close = obj.close !== false ? true : false;
            // add new tab and related content
            if (obj.close) {
                close = "<a href='javascript:void(0)' class='remove' pid='tab_" + tick + "'></a>";
            }
            $("#tabs").append("<li class='current'><a class='tab' id='tab_" + tick + "' href='javascript:void(0)'>" + obj.title +
            "</a>" + close + "</li>");

            tabs[obj.url] = 'tab_' + tick;
            $("#content").append("<iframe  id='tab_" + tick + "_content' name='right' frameborder='0' src='" + obj.url + "'  scrolling='auto' ></iframe>");
            // set the newly added tab as current
            $("#tab_" + tick + "_content").show();
        tabsId.push('tab_' + tick );


    }
