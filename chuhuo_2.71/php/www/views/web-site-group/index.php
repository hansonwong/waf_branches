<?php
use yii\helpers\Html;
use \yii\helpers\Url;
?>
<div class="list_page">
    <!--ztree strat-->
    <div class="c_l">
        <div class="gj"></div>
        <ul id="websiteTree" class="ztree"></ul>
    </div>
    <!--ztree end-->
    <div class="c_r">
        <iframe id="cList" frameborder="0" name="clist" scrolling="auto" src="<?php echo Url::to(['index']);?>"></iframe>
    </div>
</div>
<script type="text/javascript">
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
        { id:1, pId:0, name:"<?=Yii::$app->sysLanguage->getTranslateBySymbol('rootNode') ?>", open:true, //根节点
            children:[
                <?php foreach( $model as $v ): ?>
                { id:<?= $v['id'] ?>, pId:1, name:'<?= Html::encode("{$v['groupName']}") ?>',open:true,
                    children:[
                        <?php foreach( $v['webSite'] as $_v ): ?>
                        { id:<?= $_v['id'] ?>, pId:<?= $v['id'] ?>, name:'<?= Html::encode("{$_v['sWebSiteName']}") ?>'},
                        <?php endforeach; ?>
                    ]},
                <?php endforeach; ?>
            ]}
    ];

    function onClick(e,treeId, treeNode) {
        //单击展开子节点
        zTree.expandNode(treeNode);

        var _src;
        // 根结点
        if( treeNode.level===0 )
        {
            _src = "<?php echo Url::to(['index']);?>";
        }
        // 站点
        if( treeNode.level===1 )
        {
            _src = "<?php echo Url::to(['web-site/index']);?>"+'&id='+treeNode.id;
        }
        // 服务器
        if( treeNode.level===2 )
        {
            _src = "<?php echo Url::to(['web-site-servers/index']);?>"+'&id='+treeNode.id;
        }

        $('#cList').attr('src',_src);
    }

    var zTree, rMenu;
    $(document).ready(function(){
        $.fn.zTree.init($("#websiteTree"), websiteSetting, websiteNodes);
        zTree = $.fn.zTree.getZTreeObj("websiteTree");
    });
</script>
