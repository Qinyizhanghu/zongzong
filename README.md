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
