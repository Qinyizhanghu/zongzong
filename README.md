### 1 修改的地方
#### 1.1 settings.py 文件
```py
# 加入了
pymysql.version_info = (1, 3, 13, "final", 0)
```

#### 1.2 mysql 操作的文件 
参考: https://stackoverflow.com/questions/56820895/migrations-error-in-django-2-attributeerror-str-object-has-no-attribute-dec
/Users/me/QinyiZhang/zongzong/ENVZ/lib/python3.7/site-packages/django/db/backends/mysql/operations.py 文件
```py
def last_executed_query(self, cursor, sql, params):
    # With MySQLdb, cursor objects have an (undocumented) "_executed"
    # attribute where the exact query sent to the database is saved.
    # See MySQLdb/cursors.py in the source distribution.
    query = getattr(cursor, '_executed', None)
    if query is not None:
        query = errors='replace'
        #query = query.decode(errors='replace')
    return query
```

#### 1.3 V2 里面对数据表的修改
1. 修改: 用户基础信息表 UserBaseInfo, 加了 extra_info 字段
2. 新增: 探索模式下的 Banner 表 ExploreBanner
3. 新增: 商户优惠券模板表 ClubCouponTemplate
4. 修改: Footprint 表新增了 is_deleted 字段
5. 修改: Footprint 表新增了 post_type 字段
6. 修改: Footprint 表新增了 template_id 字段
7. 新增: UserCoupon 表 (用户优惠券)
8. 修改: Club 表新增了 account、password、user_info 字段
9. 修改: Club 表新增了 env_images、remark 字段
10. 删除: Club 表删除了 user_info 字段
11. 新增: 商家关联用户信息表 ClubUserInfo
12. 新增: 优惠券核销记录表 CouponChargeOffRecord
13. 修改: ActivityParticipant 表新增了 is_confirm 字段

#### 1.4 执行的更新 SQL 语句
ALTER TABLE user_info_userbaseinfo ADD extra_info varchar(1024) DEFAULT '{}' COMMENT '额外信息, json 格式';

CREATE TABLE `commercial_explorebanner` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `title` varchar(40) NOT NULL DEFAULT '' COMMENT '标题',
  `description` varchar(512) NOT NULL DEFAULT '' COMMENT '描述信息',
  `image` varchar(250) NOT NULL DEFAULT '' COMMENT '图片',
  `is_online` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否上线',
  `created_time` datetime(6) NOT NULL,
  `last_modified` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='探索模式下的 Banner';


CREATE TABLE `commercial_clubcoupontemplate` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY , 
    `name` varchar (20) NOT NULL, 
    `template_type` varchar (10) NOT NULL, 
    `money` integer UNSIGNED NOT NULL, 
    `threshold` integer UNSIGNED NOT NULL, 
    `count` integer UNSIGNED NOT NULL, 
    `balance` integer UNSIGNED NOT NULL, 
    `is_online` bool NOT NULL, 
    `deadline` datetime (6) NOT NULL, 
    `created_time` datetime (6) NOT NULL, 
    `last_modified` datetime (6) NOT NULL, 
    `club_id` integer NOT NULL
  );
ALTER TABLE `commercial_clubcoupontemplate` ADD CONSTRAINT `commercial_clubcoupo_club_id_8f217160_fk_commercia` FOREIGN KEY (`club_id`) REFERENCES `commercial_club` (`id`);

ALTER TABLE `footprint_footprint` ADD is_deleted tinyint(1) DEFAULT 0 COMMENT '是否被删除';
ALTER TABLE `footprint_footprint` ADD post_type varchar(10) DEFAULT 'note' COMMENT '帖子类型';
ALTER TABLE `footprint_footprint` ADD template_id int(11) DEFAULT 0 COMMENT '优惠券模板 id';

ALTER TABLE `commercial_club` ADD account varchar(50) DEFAULT '' COMMENT '商家账号';
ALTER TABLE `commercial_club` ADD password varchar(100) DEFAULT '' COMMENT '商家密码';
ALTER TABLE `commercial_club` ADD user_info_id int(11) COMMENT '商家账号';
ALTER TABLE `commercial_club` ADD CONSTRAINT `commercial_club_user_info_id_3cbc69eb_fk_user_info` FOREIGN KEY (`user_info_id`) REFERENCES `user_info_userbaseinfo` (`id`);
ALTER TABLE `commercial_club` DROP foreign key commercial_club_user_info_id_3cbc69eb_fk_user_info;
ALTER TABLE `commercial_club` DROP COLUMN user_info_id;


CREATE TABLE `footprint_usercoupon` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, 
    `acquire_way` varchar (10) NOT NULL, 
    `donate_user_id` integer NOT NULL, 
    `coupon_code` varchar (100) NULL, 
    `is_used` bool NOT NULL, 
    `created_time` datetime (6) NOT NULL, 
    `last_modified` datetime (6) NOT NULL, 
    `template_id` integer NOT NULL, 
    `user_id` integer NOT NULL
  );
ALTER TABLE `footprint_usercoupon` ADD CONSTRAINT `footprint_usercoupon_template_id_951887f1_fk_commercia` FOREIGN KEY (`template_id`) REFERENCES `commercial_clubcoupontemplate` (`id`);
ALTER TABLE `footprint_usercoupon` ADD CONSTRAINT `footprint_usercoupon_user_id_3c884cbe_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
CREATE INDEX `footprint_usercoupon_created_time_0c7d2d93` ON `footprint_usercoupon` (`created_time`);

ALTER TABLE `commercial_club` ADD env_images varchar(4096) DEFAULT '' COMMENT '环境图, 最多支持8张, 分号隔开';
ALTER TABLE `commercial_club` ADD remark varchar(1000) DEFAULT '' COMMENT '商家备注';

CREATE TABLE `commercial_clubuserinfo` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY , 
    `club_id` integer NOT NULL, 
    `user_info_id` integer NOT NULL,
    `created_time` datetime (6) NOT NULL, 
    `last_modified` datetime (6) NOT NULL 
  );
ALTER TABLE `commercial_clubuserinfo` ADD CONSTRAINT `commercial_clubuserinfo_club_id_8d0c937b_fk_commercial_club_id` FOREIGN KEY (`club_id`) REFERENCES `commercial_club` (`id`);
ALTER TABLE `commercial_clubuserinfo` ADD CONSTRAINT `commercial_clubuseri_user_info_id_008f4af8_fk_user_info` FOREIGN KEY (`user_info_id`) REFERENCES `user_info_userbaseinfo` (`id`);

CREATE TABLE `commercial_couponchargeoffrecord` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY , 
    `coupon_id` integer NOT NULL, 
    `user_id` integer NOT NULL, 
    `created_time` datetime (6) NOT NULL, 
    `last_modified` datetime (6) NOT NULL, 
    `club_user_id` integer NOT NULL
  );
ALTER TABLE `commercial_couponchargeoffrecord` ADD CONSTRAINT `commercial_couponcha_club_user_id_57e92a78_fk_commercia` FOREIGN KEY (`club_user_id`) REFERENCES `commercial_clubuserinfo` (`id`); 
