<!DOCTYPE HTML>
<html>
<head>
    <?php use app\widget\AdminList;
    use \yii\helpers\Url;?>
    <?=AdminList::widget(['type' => 'common-css'])?>
    <?=AdminList::widget(['type' => 'common-js'])?>
    <script>
        $(function(){
            $(document).ready(function() {
                $(".list-tab ul li").click(function(){
                    $(".list-tab ul li").removeClass('listcurrent');
                    $(this).addClass("listcurrent");
                })
            });
        });
    </script>
</head>
<body>
<div class="list_page">
    <div class="list-data">
        <div class="list-tab mar_top">
            <ul>
                <?php
                $defaultUrl = '';
                foreach ($tab as $item){
                    $class = isset($item['default']) && $item['default'] ? 'class="listcurrent"' : '';
                    $url = Url::to($item['url'] ?? []);
                    if('' != $class) $defaultUrl = $url;
                    $title = Yii::$app->sysLanguage->getTranslateBySymbol($item['title'] ?? '');
                    echo "<li {$class}><a href='{$url}' target='wcontent'>{$title}</a></li>";
                }
                ?>
            </ul>
        </div>
        <div class="list-content">
            <iframe src="<?=$defaultUrl?>" name="wcontent"  frameborder="0" width="100%" height="100%"></iframe>
        </div>
    </div>
</div>
</body>
</html>