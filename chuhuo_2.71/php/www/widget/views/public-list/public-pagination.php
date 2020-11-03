<?php
$urlPrefix = Yii::$app->sysPath->resourcePath;
$get = Yii::$app->request->get();
unset($get['page'], $get['r']);
$pageUrl = $urlPrefix.Yii::$app->requestedRoute.'?'.http_build_query($get).'&page=';

$totalCount = $pagination->totalCount;
$page = $pagination->getPage() + 1;
$pageSize = $pagination->getPageSize();
$pageCount = $pagination->getPageCount();

$jumpUrl = "<input type='number' style='width: 60px;'> <a href='javascript:;' onclick='jumpUrl(this);'>".Yii::$app->sysLanguage->getTranslateBySymbol('jumpTo')."</a>";
$totalStr = "<a href='javascript:;'>%s {$totalCount} %s,{$page}/{$pageCount}%s</a>";
$info = sprintf($totalStr,
    Yii::$app->sysLanguage->getTranslateBySymbol('total'),
    Yii::$app->sysLanguage->getTranslateBySymbol('record'),
    Yii::$app->sysLanguage->getTranslateBySymbol('page'));
//$info = "<a href=\"javascript:;\">共 {$totalCount} 记录,{$page}/{$pageCount}页</a>";
$pageShowCount = 10;
$page_half = (int) ($pageShowCount/2);


$firstPage = $lastPage = $prePage = $nextPage = '';

$start = 1;
$end = 1;
if($pageCount <= $pageShowCount){
	$start = 1;
	$end = $start + $pageCount;
}

if($page - $page_half <= 0){
	$start = 1;
} else{
	$start = $page - $page_half;
	$firstPage = "<a href=\"{$pageUrl}1\" class=''>".Yii::$app->sysLanguage->getTranslateBySymbol('pageFirst')."</a>";
}

if($page + $page_half >= $pageCount){
	$end = $pageCount;
} else{
	$end = $page + $page_half;
	$lastPage = "<a href=\"{$pageUrl}{$pageCount}\" class=''>".Yii::$app->sysLanguage->getTranslateBySymbol('pageLast')."</a>";
}

$nextPage = '';
if($page < $pageCount){
	$nextPage = $page + 1;
	$nextPage = "<a href=\"{$pageUrl}{$nextPage}\" class=''>".Yii::$app->sysLanguage->getTranslateBySymbol('pageNext')."</a>";
}

$prePage = '';
if($page > 1){
	$prePage = $page - 1;
	$prePage = "<a href=\"{$pageUrl}{$prePage}\" class=''>".Yii::$app->sysLanguage->getTranslateBySymbol('pagePrevious')."</a>";
}
?>
<div class="cl pd-5 bg-1 bk-gray mt-20">
	<div class="text-c">
		<div name="laypage1.2" class="laypage_main laypageskin_default" id="laypage_0">
			<?php
			echo $jumpUrl.$info.$firstPage.$lastPage.$prePage.$nextPage;
			for($i = $start; $i <= $end; $i++){
				if($i == $page) {
					$url = 'javascript:;';
					$class = 'active';
				} else {
					$url = $pageUrl.$i;
					$class = '';
				}
				echo "<a href=\"{$url}\" class='{$class}'>".($i)."</a>";
			}
			?>
			<!--<a href="javascript:;" class="laypage_prev" data-page="5">上一页</a>
			<a href="javascript:;" class="laypage_first" data-page="1" title="首页">1</a>
			<span>…</span><a href="javascript:;" data-page="4">4</a>
			<a href="javascript:;" data-page="5">5</a>
			<span class="laypage_curr">6</span>
			<a href="javascript:;" data-page="7">7</a><a href="javascript:;" data-page="8">8</a>
			<span>…</span>
			<a href="javascript:;" class="laypage_last" title="尾页" data-page="32">32</a>
			<a href="javascript:;" class="laypage_next" data-page="7">下一页</a>-->
		</div>
	</div>
	<div class="text-r">
		<div name="laypage1.2" class="laypage_main laypageskin_default" id="pageSizeSetting">
			<a href="javascript:;" class=""><?=Yii::$app->sysLanguage->getTranslateBySymbol('pagePerRecord')?>:</a>
			<a href="javascript:;" class="" page=15>15</a>
			<a href="javascript:;" class="" page=20>20</a>
			<a href="javascript:;" class="" page=30>30</a>
			<a href="javascript:;" class="" page=40>40</a>
			<a href="javascript:;" class="" page=0><?=Yii::$app->sysLanguage->getTranslateBySymbol('allRecord')?></a>
		</div>
		<script>
			$(function(){
				var pageSize = getUrlParam('pagesize');
				if('' != pageSize){
					$('[page=' + pageSize + ']').attr('class', 'active');
				}
				$('#pageSizeSetting a').click(function(){
					var page = $(this).attr('page');
					var url = location.href;
					url = url.replace(/&pagesize=\d*&/g, '&');
					url = url.replace(/&pagesize=\d*/g, '');
					url = url.replace(/\?pagesize=\d*&/g, '?');
					url = url.replace(/\?pagesize=\d*/g, '?');
					location.href = url + ((url.indexOf('?') != -1) ? '' : '?') + '&pagesize=' + page;
				});
			});
		</script>
	</div>
</div>
<script>
function jumpUrl(obj){
	location.href = '<?=$pageUrl?>' + $(obj).prev().val();
}
</script>
<style>
.laypageskin_default a, .laypageskin_default input {
	border: 1px solid #ddd;
	background-color: #fff;
}
.laypage_main a, .laypage_main span {
	margin: 0 3px 6px;
	padding: 0 10px;
}
.laypage_main input{
	margin: 0 3px 6px;
	text-align: right;
}
.laypage_main a, .laypage_main input {
	height: 26px;
	line-height: 26px;
	text-decoration: none;
	color: #666;
}
.laypage_main * {
	display: inline-block;
	vertical-align: top;
	font-size: 12px;
}

.laypage_main {
	font-size: 0;
	clear: both;
	color: #666;
}
.laypage_main a.active{
	background-color: #0a6999;
	color: #fff;
}
</style>