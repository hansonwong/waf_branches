<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
<?php
use \yii\helpers\Url;
use yii\helpers\Html;
use app\widget\AdminList;
$urlPrefix = Yii::$app->sysPath->resourcePath;
?>
<meta charset="utf-8">
<meta name="renderer" content="webkit|ie-comp|ie-stand">
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
<meta name="viewport" content="width=device-width,initial-scale=1,minimum-scale=1.0,maximum-scale=1.0,user-scalable=no" />
<meta http-equiv="Cache-Control" content="no-siteapp" />
<?php
$urlPrefix = Yii::$app->sysPath->resourcePath;
$staticResourcePrefix = "{$urlPrefix}assets/waf/";?>
<?=Html::csrfMetaTags()?>
<LINK rel="Bookmark" href="<?=$urlPrefix?>favicon.ico" >
<LINK rel="Shortcut Icon" href="<?=$urlPrefix?>favicon.ico" />
<!--[if lt IE 9]>
<script type="text/javascript" src="<?=$urlPrefix?>assets/h-ui/lib/html5.js"></script>
<script type="text/javascript" src="<?=$urlPrefix?>assets/h-ui/lib/respond.min.js"></script>
<script type="text/javascript" src="<?=$urlPrefix?>assets/h-ui/lib/PIE_IE678.js"></script>
<![endif]-->

<!--公共-->
<link href="<?=$staticResourcePrefix?>skin/blue/style/public.css" rel="stylesheet" type="text/css">
<link href="<?=$staticResourcePrefix?>skin/blue/style/style.css" rel="stylesheet" type="text/css">
<link href="<?=$staticResourcePrefix?>skin/blue/style/style_waf.css" rel="stylesheet" type="text/css">

<link rel="stylesheet" type="text/css" href="<?=$urlPrefix?>assets/h-ui/static/h-ui/css/H-ui.min.css" />
<link rel="stylesheet" type="text/css" href="<?=$urlPrefix?>assets/h-ui/static/h-ui.admin/css/H-ui.admin.css" />
<link rel="stylesheet" type="text/css" href="<?=$urlPrefix?>assets/h-ui/lib/Hui-iconfont/1.0.7/iconfont.css" />
<link rel="stylesheet" type="text/css" href="<?=$urlPrefix?>assets/h-ui/lib/icheck/icheck.css" />
<link rel="stylesheet" type="text/css" href="<?=$urlPrefix?>assets/h-ui/static/h-ui.admin/skin/default/skin.css" id="skin" />
<link rel="stylesheet" type="text/css" href="<?=$urlPrefix?>assets/h-ui/static/h-ui.admin/css/style.css" />
<!--[if IE 6]>
<script type="text/javascript" src="<?=$urlPrefix?>assets/h-ui/lib/DD_belatedPNG_0.0.8a-min.js" ></script>
<script>DD_belatedPNG.fix('*');</script>
<![endif]-->
<script src="<?=$urlPrefix?>assets/h-ui/lib/jquery/1.9.1/jquery.min.js"></script>


<script src="<?=$urlPrefix?>assets/h-ui/lib/layer/2.1/layer.js"></script>
<!--<script src="<?=$urlPrefix?>assets/h-ui/lib/laypage/1.2/laypage.js"></script>-->
<!--<script src="<?=$urlPrefix?>assets/h-ui/lib/My97DatePicker/WdatePicker.js"></script>-->
<script src="<?=$urlPrefix?>assets/h-ui/static/h-ui/js/H-ui.js"></script>
<script src="<?=$urlPrefix?>assets/h-ui/static/h-ui.admin/js/H-ui.admin.js"></script>

<script src="<?=$urlPrefix?>assets/h-ui/lib/bootstrap-modal/2.2.4/bootstrap-modalmanager.js"></script>
<script src="<?=$urlPrefix?>assets/h-ui/lib/bootstrap-modal/2.2.4/bootstrap-modal.js"></script>

<!--<script src="<?=$urlPrefix?>assets/h-ui/lib/icheck/jquery.icheck.min.js"></script>
<script src="<?=$urlPrefix?>assets/h-ui/lib/jquery.validation/1.14.0/jquery.validate.min.js"></script>
<script src="<?=$urlPrefix?>assets/h-ui/lib/jquery.validation/1.14.0/validate-methods.js"></script>
<script src="<?=$urlPrefix?>assets/h-ui/lib/jquery.validation/1.14.0/messages_zh.min.js"></script>-->


<title></title>

<link rel="StyleSheet" href="<?=$urlPrefix?>assets/js/dtree/dtree.css" type="text/css" />
<script>var dtreeImgPath = '<?=$urlPrefix?>assets/js/dtree/img/';</script>
<script src="<?=$urlPrefix?>assets/js/dtree/dtree.js"></script>

<script src="<?=$urlPrefix?>assets/js/common.js"></script>
</head>
<body>
<div class="page-container">
	<div class="row cl">
		<div class="col-xs-12 col-sm-12">
			<a class="btn btn-success" href="javascript: d.openAll();"><?=Yii::$app->sysLanguage->getTranslateBySymbol('allExpand')?></a>
			<a class="btn btn-success" href="javascript: d.closeAll();"><?=Yii::$app->sysLanguage->getTranslateBySymbol('allExpandOff')?></a>
			<a class="btn btn-success" href="javascript:location.replace(location.href);" title="<?=Yii::$app->sysLanguage->getTranslateBySymbol('refresh')?>" ><i class="Hui-iconfont">&#xe68f;</i></a>
		</div>
	</div>

	<div class="row cl">
		<div class="dtree container">
			<div class="col-xs-12 col-sm-12"><br>
				<script>
					d = new dTree('d');

					d.add(0,-1, 'TOP', 'javascript:operation(0, &quot;TOP&quot;);');
					<?php
					foreach($data as $item){
						$icon = (0 == $item['enable']) ? "{$urlPrefix}assets/js/dtree/img/no.png" : "{$urlPrefix}assets/js/dtree/img/yes.png";
						$icon = "<span><img src={$icon}></span>";
						echo "d.add(
					{$item['id']},
					{$item['parent_id']},
					'{$item['name']}{$icon}',
					'javascript:operation({$item['id']}, &quot;{$item['name']}&quot;);',
					'{$item['descr']}'
					);";
					}
					?>
					document.write(d);
				</script>
			</div>
		</div>
	</div>
</div>
<div id="myModal" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
	<div class="modal-header">
		<h5 id="myModalLabel"></h5><a class="close" data-dismiss="modal" aria-hidden="true" href="javascript:void();">×</a>
	</div>
	<div class="modal-body">
		<div id="tab_demo" class="HuiTab">
			<div class="tabBar cl">
                <span><?=Yii::$app->sysLanguage->getTranslateBySymbol('update')?></span>
                <span><?=Yii::$app->sysLanguage->getTranslateBySymbol('create')?></span></div>
			<div class="tabCon">

				<form id="update" method="post" class="form form-horizontal" onsubmit="if(event.keyCode==13){return false;}">
					<legend><?=Yii::$app->sysLanguage->getTranslateBySymbol('update')?></legend>
					<input type=hidden name=id>
					<input type=hidden name=<?=$model->modelName?>[id]>
					<input type=hidden name=<?=$model->modelName?>[parent_id]>
					<input type="hidden" name="_csrf" value=""/>
					<div class="row cl">
						<label class="form-label col-xs-4 col-sm-3"><?=Yii::$app->sysLanguage->getTranslateBySymbol('menuName')?>：</label>
						<div class="formControls col-xs-8 col-sm-9">
							<input type=text class="input-text" name=<?=$model->modelName?>[name]>
						</div>
					</div>
					<div class="row cl">
						<label class="form-label col-xs-4 col-sm-3"><?=Yii::$app->sysLanguage->getTranslateBySymbol('visitPath')?>：</label>
						<div class="formControls col-xs-8 col-sm-9">
							<input type=text class="input-text" name=<?=$model->modelName?>[url]>
						</div>
					</div>

					<div class="row cl">
						<label class="form-label col-xs-4 col-sm-3"><?=Yii::$app->sysLanguage->getTranslateBySymbol('enable')?>：</label>
						<div class="formControls col-xs-8 col-sm-9">
							<span class="select-box">
							<select class=select size=1 name=<?=$model->modelName?>[enable]>
								<option value="1"><?=Yii::$app->sysLanguage->getTranslateBySymbol('enable')?></option>
								<option value="2"><?=Yii::$app->sysLanguage->getTranslateBySymbol('enable')?>(<?=Yii::$app->sysLanguage->getTranslateBySymbol('hide')?>)</option>
								<option value="0"><?=Yii::$app->sysLanguage->getTranslateBySymbol('disable')?></option>
							</select>
							</span>
						</div>
					</div>

                    <div class="row cl">
                        <label class="form-label col-xs-4 col-sm-3"><?=Yii::$app->sysLanguage->getTranslateBySymbol('isDisplayChildMenu')?>：</label>
                        <div class="formControls col-xs-8 col-sm-9">
							<span class="select-box">
							<select class=select size=1 name=<?=$model->modelName?>[display_child]>
								<option value="1"><?=Yii::$app->sysLanguage->getTranslateBySymbol('yes')?></option>
								<option value="0"><?=Yii::$app->sysLanguage->getTranslateBySymbol('no')?></option>
							</select>
							</span>
                        </div>
                    </div>

					<div class="row cl">
						<label class="form-label col-xs-4 col-sm-3"><?=Yii::$app->sysLanguage->getTranslateBySymbol('sort')?>：</label>
						<div class="formControls col-xs-8 col-sm-9">
							<input type=text class="input-text" name=<?=$model->modelName?>[sort]>
						</div>
					</div>
					<div class="row cl">
						<label class="form-label col-xs-4 col-sm-3"><?=Yii::$app->sysLanguage->getTranslateBySymbol('description')?>：</label>
						<div class="formControls col-xs-8 col-sm-9">
							<input type=text class="input-text" name=<?=$model->modelName?>[descr]>
						</div>
					</div>
                    <div class="row cl">
                        <label class="form-label col-xs-4 col-sm-3">ICON CLASS：</label>
                        <div class="formControls col-xs-8 col-sm-9">
                            <input type=text class="input-text" name=<?=$model->modelName?>[icon_class]>
                        </div>
                    </div>
					<div class="row cl">
						<div class="col-xs-8 col-sm-9 col-xs-offset-4 col-sm-offset-3">
							<a class="btn btn-primary" onclick="updateTree('update', '<?=Url::to(['update'])?>');"><?=Yii::$app->sysLanguage->getTranslateBySymbol('update')?></a>
						</div>
					</div>
				</form>

			</div>
			<div class="tabCon">
				<form id="create" method="post" class="form form-horizontal" onsubmit="if(event.keyCode==13){return false;}">
					<legend><?=Yii::$app->sysLanguage->getTranslateBySymbol('create')?></legend>
					<input type="hidden" name="_csrf" value=""/>
					<input type=hidden name=<?=$model->modelName?>[id]>
					<input type=hidden name=<?=$model->modelName?>[parent_id]>
					<div class="row cl">
						<label class="form-label col-xs-4 col-sm-3"><?=Yii::$app->sysLanguage->getTranslateBySymbol('menuName')?>：</label>
						<div class="formControls col-xs-8 col-sm-9">
							<input type=text class="input-text" name=<?=$model->modelName?>[name]>
						</div>
					</div>
					<div class="row cl">
						<label class="form-label col-xs-4 col-sm-3"><?=Yii::$app->sysLanguage->getTranslateBySymbol('visitPath')?>：</label>
						<div class="formControls col-xs-8 col-sm-9">
							<input type=text class="input-text" name=<?=$model->modelName?>[url]>
						</div>
					</div>

					<div class="row cl">
						<label class="form-label col-xs-4 col-sm-3"><?=Yii::$app->sysLanguage->getTranslateBySymbol('enable')?>：</label>
						<div class="formControls col-xs-8 col-sm-9">
							<span class="select-box">
							<select class=select size=1 name=<?=$model->modelName?>[enable]>
								<option value="1"><?=Yii::$app->sysLanguage->getTranslateBySymbol('enable')?></option>
								<option value="2"><?=Yii::$app->sysLanguage->getTranslateBySymbol('enable')?>(<?=Yii::$app->sysLanguage->getTranslateBySymbol('hide')?>)</option>
								<option value="0"><?=Yii::$app->sysLanguage->getTranslateBySymbol('disable')?></option>
							</select>
							</span>
						</div>
					</div>

                    <div class="row cl">
                        <label class="form-label col-xs-4 col-sm-3"><?=Yii::$app->sysLanguage->getTranslateBySymbol('isDisplayChildMenu')?>：</label>
                        <div class="formControls col-xs-8 col-sm-9">
							<span class="select-box">
							<select class=select size=1 name=<?=$model->modelName?>[display_child]>
								<option value="0"><?=Yii::$app->sysLanguage->getTranslateBySymbol('no')?></option>
                                <option value="1"><?=Yii::$app->sysLanguage->getTranslateBySymbol('yes')?></option>
							</select>
							</span>
                        </div>
                    </div>

					<div class="row cl">
						<label class="form-label col-xs-4 col-sm-3"><?=Yii::$app->sysLanguage->getTranslateBySymbol('sort')?>：</label>
						<div class="formControls col-xs-8 col-sm-9">
							<input type=text class="input-text" name=<?=$model->modelName?>[sort]>
						</div>
					</div>
					<div class="row cl">
						<label class="form-label col-xs-4 col-sm-3"><?=Yii::$app->sysLanguage->getTranslateBySymbol('description')?>：</label>
						<div class="formControls col-xs-8 col-sm-9">
							<input type=text class="input-text" name=<?=$model->modelName?>[descr]>
						</div>
					</div>
                    <div class="row cl">
                        <label class="form-label col-xs-4 col-sm-3">ICON CLASS：</label>
                        <div class="formControls col-xs-8 col-sm-9">
                            <input type=text class="input-text" name=<?=$model->modelName?>[icon_class]>
                        </div>
                    </div>
					<div class="row cl">
						<div class="col-xs-8 col-sm-9 col-xs-offset-4 col-sm-offset-3">
							<a class="btn btn-primary" onclick="updateTree('create', '<?=Url::to(['create'])?>');"><?=Yii::$app->sysLanguage->getTranslateBySymbol('create')?></a>
						</div>
					</div>
				</form>

			</div>
		</div>
	</div>
	<div class="modal-footer">
		<button class="btn btn-primary btn-danger" onclick="deleteTree();"><?=Yii::$app->sysLanguage->getTranslateBySymbol('delete')?></button>
		<button class="btn" data-dismiss="modal" aria-hidden="true"><?=Yii::$app->sysLanguage->getTranslateBySymbol('close')?></button>
	</div>
</div>
</body>
<style>
	.dtree .dTreeNode a>span>img{width:16px;}
</style>
<script>
	$(function(){
		$('[name=_csrf]').val($('meta[name=csrf-token]').attr('content'));
		$.Huitab("#tab_demo .tabBar span","#tab_demo .tabCon","current","click","0");
	});
	function operation(id, title){
		$('#myModalLabel').text(title).attr('data', id);
		var model = '<?=$model->modelName?>';
		if(0 == id){
			$('#update [name=id]').val('');
			$('#update [name="' + model + '[id]"]').val('');
			$('#create [name="' + model + '[parent_id]"]').val(id);

			$('#update [name="' + model + '[name]"]').val('');
			$('#update [name="' + model + '[url]"]').val('');
			$('#update [name="' + model + '[enable]"]').val('');
            $('#update [name="' + model + '[display_child]"]').val('');
			$('#update [name="' + model + '[sort]"]').val('');
			$('#update [name="' + model + '[descr]"]').val('');
            $('#update [name="' + model + '[icon_class]"]').val('');
			$('#myModal').modal('toggle');
		} else {
			$.ajax({
				url: '<?=Url::to(['one'])?>',
				type: 'POST',
				data: {
					id	: $('#myModalLabel').attr('data'),
					_csrf   : $('meta[name=csrf-token]').attr('content'),
				},
				dataType: 'json',
				timeout: 5000,//1000毫秒后超时
				cache: false,//不缓存数据
				async: false,//同步：false,异步：true,默认true
				success: function(data){
				    if(!data.success) return;

				    var item = data.data;

					$('#create [name="' + model + '[parent_id]"]').val(item.id);

					$('#update [name=id]').val(item.id);
					$('#update [name="' + model + '[id]"]').val(item.id);
					$('#update [name="' + model + '[parent_id]"]').val(item.parent_id);

					$('#update [name="' + model + '[name]"]').val(item.name);
					$('#update [name="' + model + '[url]"]').val(item.url);
					$('#update [name="' + model + '[enable]"]').val(item.enable);
                    $('#update [name="' + model + '[display_child]"]').val(item.display_child);
					$('#update [name="' + model + '[sort]"]').val(item.sort);
					$('#update [name="' + model + '[descr]"]').val(item.descr);
                    $('#update [name="' + model + '[icon_class]"]').val(item.icon_class);
					$('#myModal').modal('toggle');
				},//请求成功后执行
				error: function(){
					alert('<?=Yii::$app->sysLanguage->getTranslateBySymbol('networkTimeout')?>');
				}
			});
		}
	}

	function updateTree(id, url){
		$.ajax({
			url: url + '&id=' + $('#update [name="<?=$model->modelName?>[id]"]').val(),
			type: 'POST',
			data: $('#' + id).serialize(),
			dataType: 'json',
			timeout: 5000,//1000毫秒后超时
			cache: false,//不缓存数据
			async: false,//同步：false,异步：true,默认true
			success: function(data){
				alert(data.msg);
				if(true === data.success){
					location.reload();
				}
			},//请求成功后执行
		});
	}

	function deleteTree(){
		if(!confirm('<?=Yii::$app->sysLanguage->getTranslateBySymbol('isDeleteThisMenu')?>?')) return;
        $.ajax({
            url: '<?=Url::to(['delete'])?>',
            type: 'POST',
            data: {
                id	: $('#myModalLabel').attr('data'),
                _csrf   : $('meta[name=csrf-token]').attr('content'),
            },
            dataType: 'json',
            timeout: 5000,//1000毫秒后超时
            cache: false,//不缓存数据
            async: false,//同步：false,异步：true,默认true
            success: function(data){
                alert(data.msg);
                if(true === data.success){
                    location.reload();
                }
            },//请求成功后执行
        });
	}
</script>
</html>