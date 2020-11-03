//editor 姚秀萍
$(document).ready(function() {	
//改变语言版本开始
    $(".language").click(function(){
			$(".language").css("background-color","#154873");
			$(".language").css("color","#c6ddef");
			$(".lang").toggle();	
		}
		
		);
	
	$(".lang ul li").click(function(){
		var ltext = $(this).text()
		$(this).parent().parent().toggle();
		$(".language").html(ltext);
		$(".language").css("background-color","#0770b2");
		$(".language").css("color","#dceaf5");
		
	});
//改变语言版本结束	

    //左菜单开始
    //change by linfang 2017/11/20
    $(".menu>ul li a ").click(function() {
        $(".menu p").css('font-weight','normal');
        $(".menu>ul li a p").removeClass("aselec");
        $(".sel").removeClass();
        $(".aselec").removeClass();
        $(this).children("p").addClass("aselec").removeAttr("style");
    })
    $(".menu ul li ul ").each(function() {
        $(this).first('li').css("border-top","none")
    });
    $(".menu ul li:has(ul)").find("ul").hide();
    $(".menu ul li:has(ul) a").click(function(){
        if($(this).siblings().is(':hidden')){
            $(this).children('.menu_s').css("background-position","0px -8px");
            $(this).children('.menu_s').css("width","7px");
            $(this).children('.menu_s').css("height","4px");
            $(this).siblings().stop().slideToggle();
        }else{
            $(this).children('.menu_s').css("background-position","0px 0px");
            $(this).children('.menu_s').css("width","4px");
            $(this).children('.menu_s').css("height","7px");
            $(this).siblings().stop().slideToggle();

        }
    });
    $(".menu>ul>li>ul>li").hover(function(){
        $(this).siblings().removeClass("twoli");
        $(this).toggleClass("twoli");
    });

    $(".menu>ul>li>ul>li>ul").hover(function(){
        $(this).parents("li").toggleClass("twoli");
        $(this).parents("li").toggleClass("hower");
        $(this).siblings("a").removeClass("sel");
    });
    $(".menu ul li ul li a").click(function(){
        $(".sel").removeClass();
        $(".hower").removeClass();
        $(this).addClass("sel").parents().siblings().removeClass("sel");
    });


    // $(".menu>ul li a ").click(function() {
    //     $(".menu>ul li a p").removeClass("aselec");
    //     $(".sel").removeClass()
    //     $(this).children("p").addClass("aselec");
    // })
    // $(".menu ul li ul ").each(function() {
    //     $(this).first('li').css("border-top","none")
    // });
    // $(".menu ul li:has(ul)").find("ul").hide();
    // $(".menu ul li:has(ul) a").click(function(){
    //     if($(this).siblings().is(':hidden')){
    //         $(this).children('.menu_s').css("background-position","0px -8px");
    //         $(this).children('.menu_s').css("width","7px");
    //         $(this).children('.menu_s').css("height","4px");
    //         $(this).siblings().show()
    //     }else{
    //         $(this).children('.menu_s').css("background-position","0px 0px");
    //         $(this).children('.menu_s').css("width","4px");
    //         $(this).children('.menu_s').css("height","7px");
    //         $(this).siblings().hide()
    //
    //     }
    // });
    // $(".menu>ul>li>ul>li").hover(function(){
    //     $(this).siblings().removeClass("twoli");
    //     $(this).toggleClass("twoli");
    // });
    //
    // $(".menu>ul>li>ul>li>ul").hover(function(){
    //     $(this).parents("li").toggleClass("twoli");
    //     $(this).parents("li").toggleClass("hower");
    //     $(this).siblings("a").removeClass("sel");
    // });
    // $(".menu ul li ul li a").click(function(){
    //     $(".sel").removeClass();
    //     $(".hower").removeClass();
    //     $(this).addClass("sel").parents().siblings().removeClass("sel");
    // });



//隐藏显示左菜单
	$(".l_icon").click(function(){
	//隐藏左菜单
		if($(".menu").is(":visible")){
		 $(".menu").hide()
		 $(".menu").css("left","-200px")
		 $(".left_h").css("left","2px")
		 $(".content").css("left","10px")
		 $(".hidden_i").removeClass()
		 $(this).addClass("display_i");
		 $(this).addClass("l_icon")
		}else{   //显示左菜单
		 $(".menu").show()
		 $(".menu").css("left","0px")
		 $(".left_h").css("left","222px")
		 $(".content").css("left","230px")
		 $(".display_i").removeClass()
		 $(this).addClass("hidden_i");
		 $(this).addClass("l_icon")
		}
	});
//隐藏显示右上角菜单（告警、主页、账户）
	$(".xxts").hide();
	$(".warning").click(function(){
		if($(this).hasClass("minM_sel_w")){
			$(this).addClass("warning");
		}else{
			$(this).removeClass("warning");
		}
		$(this).toggleClass("minM_sel_w");
		$("#user").hide();
		$("#warnning").toggle();
		$(".minM_sel_u").removeClass().addClass("user");
		$(".minM_sel_h").removeClass().addClass("home");
		
	});
	
	$(".user").click(function(){
		if($(this).hasClass("minM_sel_u")){
			$(this).addClass("user");
		}else{
			$(this).removeClass("user");
		}
		$(this).toggleClass("minM_sel_u");
		
		$("#warnning").hide();
		$("#user").toggle();
		$(".minM_sel_w").removeClass().addClass("warning");
		$(".minM_sel_h").removeClass().addClass("home");
	});
	
	$(".home").click(function(){
		if($(this).hasClass("minM_sel_h")){
			$(this).addClass("home");
		}else{
			$(this).removeClass("home");
		}
		$(this).toggleClass("minM_sel_h");
		
		addTab($(this).children('a'));
		$("#warnning").hide();
		$("#user").hide();
		$(".minM_sel_w").removeClass().addClass("warning");
		$(".minM_sel_u").removeClass().addClass("user");
	});
	
	$(".xxts li").click(function(){
		addTab($(this).children('a'));
		$(".xxts").hide();
		$(".minM_sel_w").removeClass().addClass("warning");
		$(".minM_sel_u").removeClass().addClass("user");
		
	})
  
 
   
  function showtime(){
   var mydate = new Date();
   var str = "" + mydate.getFullYear() + "年";
   str += (mydate.getMonth()+1) + "月";
   str += mydate.getDate() + "日";
   str += mydate.getHours() + "时";
   str += mydate.getMinutes() + "分";
   str += mydate.getSeconds() + "秒";
   return str;
  }
  $("#showtime").html(showtime())
  
 //首页下拉式选择框	
 //统计方式
  $(".fsi1").click(function(){
	 $(".fs1").toggle();	
   });
	
  $(".fs1 ul li").click(function(){
	var ltext = $(this).text()
	$(this).parent().parent().toggle();
	$(".f1").html(ltext);
	
	});
 //统计方式
  $(".fsi2").click(function(){
	 $(".fs2").toggle();	
   });
	
  $(".fs2 ul li").click(function(){
	var ltext = $(this).text()
	$(this).parent().parent().toggle();
	$(".f2").html(ltext);
	
	});
 //统计时间 活跃主机统计
  $(".sji1").click(function(){
	 $(".sj1").toggle();	
   });
	
  $(".sj1 ul li").click(function(){
	var ltext = $(this).text()
	$(this).parent().parent().toggle();
	$(".s1").html(ltext);
	
	});
 //统计时间 报警类型统计分布
  $(".sji2").click(function(){
	 $(".sj2").toggle();	
   });
	
  $(".sj2 ul li").click(function(){
	var ltext = $(this).text()
	$(this).parent().parent().toggle();
	$(".s2").html(ltext);
	
	});

 //统计时间 访问类型统计
  $(".sji3").click(function(){
	 $(".sj3").toggle();	
   });
	
  $(".sj3 ul li").click(function(){
	var ltext = $(this).text()
	$(this).parent().parent().toggle();
	$(".s3").html(ltext);
	
	});
 //统计时间 木马报警统计分析
  $(".sji4").click(function(){
	 $(".sj4").toggle();	
   });
	
  $(".sj4 ul li").click(function(){
	var ltext = $(this).text()
	$(this).parent().parent().toggle();
	$(".s4").html(ltext);
	
	});
	
// change by Siven 修改 getElementsByClassName 在ie8以下 无效问题
  var getElementsByClassName = function (searchClass, node,tag) {
    if(document.getElementsByClassName){
      var nodes = (node || document).getElementsByClassName(searchClass),result = [];
      for(var i=0 ;node = nodes[i++];){
        if(tag !== "*" && node.tagName === tag.toUpperCase()){
          result.push(node)
        }else{
          result.push(node)
        }
      }
      return result
    }else{
      node = node || document;
      tag = tag || "*";
      var classes = searchClass.split(" "),
        elements = (tag === "*" && node.all)? node.all : node.getElementsByTagName(tag),
        patterns = [],
        current,
        match;
      var i = classes.length;
      while(--i >= 0){
        patterns.push(new RegExp("(^|\s)" + classes[i] + "(\s|$)"));
      }
      var j = elements.length;
      while(--j >= 0){
        current = elements[j];
        match = false;
        for(var k=0, kl=patterns.length; k<kl; k++){
          match = patterns[k].test(current.className);
          if (!match) break;
        }
        if (match) result.push(current);
      }
      return result;
    }
  }

//  end
})