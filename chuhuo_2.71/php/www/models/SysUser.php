<?php
namespace app\models;

use Yii;
use yii\web\IdentityInterface;
use app\widget\AdminListConfig;
use app\logic\model\tools\SelectList;

class SysUser extends \app\logic\model\BaseModel implements IdentityInterface
{
	public $pwd_confirm = null;
	public $pwd_old = null;

	public static function tableName()
	{
		return 'sys_user';
	}

	public function rulesSource()
	{
		return [
			[['id'], 'integer'],
			[['group_id', 'enable', 'error_count', 'error_lock_time'], 'integer'],
			[['name'], 'string', 'min' => 3, 'max' => 16],
            [['name'], function($attribute, $params){
                $tips = Yii::$app->sysLanguage->getTranslateBySymbol('userNameLimitType');
                preg_match('/^[\da-zA-Z]*$/', $this->$attribute, $matches, PREG_OFFSET_CAPTURE);
                if(!isset($matches[0][0])) $this->addError($attribute, $tips);
            }],
            [['name'], 'unique'],
            [['name', 'group_id', 'enable'], 'required'],
			[['pwd'], 'string', 'max' => 16],
            [['pwd', 'pwd_confirm', 'pwd_old',], 'safe'],
			[['pwd'], 'required', 'on' => 'create'],
            [['pwd'], 'pwdCheckValidate', 'skipOnEmpty' => false],
            [['pwd_up_time', 'login_time',], 'default', 'value' => 0],
		];
	}

    /**
     * 验证密码输入
     * @param $attribute
     * @param $params
     */
	public function pwdCheckValidate($attribute, $params) {
	    $pwdError = Yii::$app->sysLanguage->getTranslateBySymbol('newPwdAndConfirmPwdNotEqual');
        if ('' === $this->pwd_confirm || null === $this->pwd_confirm){
            if('' != $this->$attribute) $this->addError($attribute, $pwdError);
            $this->offsetUnset($attribute);
        } else {
            if($this->pwd_confirm != $this->$attribute)
                $this->addError($attribute, $pwdError);
            else {
                $result = PasswordPolicy::validatePwd($this->$attribute);
                if(true !== $result) $this->addError($attribute, $result);
                $this->$attribute = self::pwdMake($this->$attribute);
                $this->pwd_up_time = time();
            }
        }
    }

    /**
     * 生成密码
     * @param $pwd
     * @return string
     */
    public static function pwdMake($pwd){
	    return md5($pwd);
    }

	public function search($params)
	{
		$query = $this->find();
		$this->load($params);
		$condition = [
            '=' => ['group_id', 'enable',],
            '~' => ['name',],
        ];
        if(!Yii::$app->sysLogin->isSuperAdmin()) $condition['!='] = ['group_id' => 1];
        $this->searchFilterHelper($query, $this, $condition);
		return ['query' => $query];
	}

	public function beforeSave($insert)
	{
		if (parent::beforeSave($insert)) {
		    #非超级管理员,不能创建或更新为超级管理员角色
		    if(!Yii::$app->sysLogin->isSuperAdmin() && 1 == $this->group_id) return false;
			return true;
		} else {
			return false;
		}
	}

	public function afterSave($insert, $changedAttributes)
    {
        parent::afterSave($insert, $changedAttributes);
        #同步账号到防火墙系统中
        \app\logic\firewall\FirewallUser::userCreateModify($this);
    }

    public function beforeDelete()
    {
        $user = Yii::$app->sysLogin->getUser();
        if($this->name == $user->name) return false;
        if($this->id == 1) return false;
        if(!Yii::$app->sysLogin->isSuperAdmin() && 1 == $this->group_id) return false;
        #从防火墙系统中删除相应账号
        \app\logic\firewall\FirewallUser::deleteFirewallUser($this);
        return true;
    }

    public function attributeLabelsSource()
	{
		return [
			'id' => 'ID',
			'name' => '用户名',
            'pwd_old' => '旧密码',
			'pwd' => '密码',
            'pwd_confirm' => '确认密码',
			'group_id' => '属组',
			'enable' => '可用',
		];
	}

	public function getSysUserGroup()
	{
		return $this->hasOne(SysUserGroup::className(), ['id' => 'group_id']);
	}

	public function ListSearch()
	{
        return [
            'field' => ['name',
                'group_id' => SelectList::systemUserGroup('select'),
                'enable' => SelectList::enable('select'),
            ],
            'key' => $this->modelName,
            'model' => $this,
        ];
	}

	public function ListTable()
	{
        return [
            #'publicButton' => ['create' => ['href' => 'http://www.www.com', 'target' => '_blank', 'title' => 'www', 'authority' => 'xxx/xxx']],
            'field' => [//'id' => ['sort' => true, 'float' => 'r'],//不显示主键
                'name',
                'group_id' => [
                    'type' => 'switch', 'val' => SelectList::systemUserGroup('switch')
                    /*'type' => 'foreignKey', 'val' => 'sysUserGroup:group_name'*/],
                'enable' => ['float' => 'c', 'type' => 'switch', 'val' => SelectList::enable('switch')],
            ],
            /*'recordOperation' => [
                ['title' => '按钮', 'url' => ['/supplier-account/index?SupplierAccount[supplier_id]=%s&ee=%s', 'id', 'name'], 'type' => 'blank', 'authority' => 'supplier-account/index']
            ],*/
            'model' => $this,
        ];
	}

	public function ListField()
	{
		$type = AdminListConfig::ListFieldScenarios('common', $this);
		$fieldKey = $this->modelName;

		$fieldType = [
		    'id' => ['showType' => 'hidden'],
		    'pwd_old' => ['showType' => 'hidden'],
            'pwd' => ['type' => 'password', 'default' => ''],
            'pwd_confirm' => ['type' => 'password'],
            //'pwd'   => ['type' => 'textarea', 'length' => 0, 'height' => '150px'],
            //'name'  => ['type' => 'textarea-editor'],
            //'name'  => ['type' => 'timepicker', 'timeFormat' => 'yy-mm-dd', 'dateFormat' => 'HH:mm:ss'],
            //'pwd'   => ['type' => 'radio', 'data' => ['1' => '男', '2' => '女']],
            //'pwd'   => ['type' => 'checkbox', 'data' => ['1' => '苹果', '2' => '苹果树']],
            //'pwd'    => ['type' => 'file', 'exts' => 'jpg,png,gif,jpeg', 'size' => 2048, 'fileType' => 'img', 'imgPx' => ''],
            'group_id' => SelectList::systemUserGroup('select'),
            'enable' => SelectList::enable('select'),
        ];
		switch ($type) {
			case 'create' :
				break;
			case 'update' :
                $fieldType['name']['showType'] = 'show';
				break;
			default :
				;
		}
        $field = [
            'fieldKey' => $fieldKey,
            'field' => $this->attributeLabels(),
            'fieldType' => $fieldType,
            'customStr' => false,
        ];
		return $field;
	}

	/**
	 * @inheritdoc
	 */
	public static function findIdentity($id)
	{
		return static::findOne(['id' => $id, 'enable' => 1]);
	}

	/**
	 * Finds user by username
	 *
	 * @param string $username
	 * @return static|null
	 */
	public static function findByUsername($username)
	{
		return static::findOne(['name' => $username, 'enable' => 1]);
	}

	/**
	 * @inheritdoc
	 */
	public function getId()
	{
		return $this->getPrimaryKey();
	}

	/**
	 * @inheritdoc
	 */
	public function getAuthKey()
	{
		return '';
	}

	/**
	 * Validates password
	 *
	 * @param string $password password to validate
	 * @return boolean if password provided is valid for current user
	 */
	public function validatePassword($password)
	{
	    $pwd = \app\logic\firewall\FirewallUser::authcode($password);
		return ($this->pwd == self::pwdMake($pwd)) ? true : false;
	}

    /**
     * 验证密码是否匹配,密码无加密情况下
     * @param $password
     * @return bool
     */
    public function validatePasswordForNoAuthcode($password)
    {
        return ($this->pwd == self::pwdMake($password)) ? true : false;
    }

	/**
	 * @inheritdoc
	 */
	public function validateAuthKey($authKey)
	{
		return $this->getAuthKey() === $authKey;
	}

	/**
	 * @inheritdoc
	 */
	public static function findIdentityByAccessToken($token, $type = null)
	{
		throw new NotSupportedException('"findIdentityByAccessToken" is not implemented.');
	}
}
