<?php
namespace app\models;

use Yii;
use app\widget\AdminListConfig;
use app\logic\model\BaseModel;;

/**
 * This is the model class for table "sys_user".
 *
 * @property integer $id
 * @property string $name
 * @property string $pwd
 * @property integer $group_id
 */
class SlideLoop extends BaseModel
{
	public static function tableName()
	{
		return 'slide_loop';
	}

	public function rulesSource()
	{
		return [
			[['sort'], 'integer'],
			[['title', 'descr'], 'string', 'max' => 255],
			[['display'], 'string', 'max' => 1],
			[['img', 'url'], 'string', 'max' => 1000],
		];
	}

	public function attributeLabelsSource()
	{
		return [
			'id' => 'ID',
			'title' => '标题',
			'descr' => '描述',
			'img' => '图片链接',
			'url' => '链接',
			'display' => '显示',
			'sort' => '排序',
		];
	}

	public function search($params)
	{
		$query = $this->find();
		$this->load($params);
        $this->searchFilterHelper($query, $this, [
            '=' => ['id', 'display',],
            '~' => ['title', 'descr',],
        ]);
        return ['query' => $query];
	}

	/**
	 * 搜索配置
	 * @return array
	 */
	public function ListSearch()
	{
        return [
            'field' => ['id', 'title','descr',
                'display' => $this->returnDisplay('select'),
            ],
            'key' => $this->modelName,
            'model' => $this,
        ];
	}

	public function ListTable()
	{
        return [
            'field' => ['id' => ['sort' => true, 'float' => 'r'], 'title','descr',
                'display' => ['float' => 'c', 'type' => 'switch', 'val' => $this->returnDisplay('switch')],
                'sort' => ['sort' => true, 'float' => 'r']
            ],
            'model' => $this,
        ];
	}

	/**
	 * 字段修改、添加配置
	 * @return array
	 */
	public function ListField()
	{
		$type = AdminListConfig::ListFieldScenarios('common', $this);
		$fieldKey = $this->modelName;

        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => [
                'id' => ['showType' => 'hidden'],
                'display' => $this->returnDisplay('select'),
            ],
            'customStr' => false,
        ];
		switch ($type) {
			case 'create' :
				break;
			case 'update' :
				break;
			default :
				;
		}
		return $field;
	}

	public function returnDisplay($type)
	{
		$arr = ['1' => '是', '0' => '否'];
		return AdminListConfig::returnSelect($type, $arr);
	}

	public static function getEnableAll()
	{
		return self::find()->where(['display' => '1'])->orderBy('sort asc')->all();
	}
}
