

    var websiteSetting = {
      view: {
        dblClickExpand: false
      },
      check: {
        enable: false
      },
      callback: {
          onClick: onClick
      },
      data: {
        simpleData: {
          enable: true
        }
      }
    };

    var websiteNodes =[
      { id:1, pId:0, name:"根节点", open:true,
        children:[
          { id:11, pId:1, name:"反向代理站点",
            children:[
              { id:111, pId:11, name:"wwww.lyx.com"},
              { id:112, pId:11, name:"wwww.test.com"},
            ]},
          { id:12, pId:1, name:"未分类站点",
            children:[
              { id:121, pId:12, name:"192.168.1.177"},
              { id:122, pId:12, name:"192.168.1.177"},
            ]},
          { id:13, pId:1, name:"未分类服务器",open:true,
            children:[
              { id:131, pId:13, name:"wwww.lyx.com"},
              { id:132, pId:13, name:"wwww.lyx.com"},
              { id:133, pId:13, name:"wwww.lyx.com"},
              { id:134, pId:13, name:"192.168.1.177"},
              { id:135, pId:13, name:"192.168.1.177"}
            ]}
        ]}
    ];



    function onClick(e,treeId, treeNode) {
      //单击展开子节点
      zTree.expandNode(treeNode);

    }


    var zTree, rMenu;
    $(document).ready(function(){
     $.fn.zTree.init($("#websiteTree"), websiteSetting, websiteNodes);
      zTree = $.fn.zTree.getZTreeObj("websiteTree");  
    });
