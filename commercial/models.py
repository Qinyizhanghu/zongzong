from django.db import models
from django.db.models import ForeignKey

from commercial.const import CouponTemplateChoices
from user_info.models import UserBaseInfo


class Club(models.Model):
    # 俱乐部名称
    def __unicode__(self):
        return '{name}_{id}'.format(name=self.name, id=self.id)

    class Meta:
        verbose_name = u'商家'
        verbose_name_plural = u'商家'

    name = models.CharField(max_length=40, verbose_name='俱乐部名称')
    fans_num = models.PositiveIntegerField(default=0, verbose_name='粉丝数量')
    address = models.CharField(max_length=100, verbose_name='地址 ')
    business_type = models.CharField(max_length=200, verbose_name='业务类型')
    representative = models.CharField(max_length=20, verbose_name='法人代表')
    avatar = models.ImageField(verbose_name='头像', blank=True, null=True)
    telephone = models.CharField(max_length=15, verbose_name='电话')
    lat = models.FloatField(verbose_name='维度')
    lon = models.FloatField(verbose_name='经度')

    # @zhanghu
    account = models.CharField(max_length=50, verbose_name='商家账号')
    password = models.CharField(max_length=100, verbose_name='商家密码')
    # 用户第一次进入商家的时候, 需要使用账号和密码登录认证, 同时, 把对应的 user_info 存到这里, 一个 Club 可以对应多个 user_info
    user_info = ForeignKey(UserBaseInfo, on_delete=models.CASCADE, verbose_name='用户信息')

    created_time = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)


class CommercialActivity(models.Model):
    # 商业活动
    def __unicode__(self):
        return '{name}_{start_time}'.format(name=self.name, start_time=self.time_detail)
    club = ForeignKey(Club, on_delete=models.CASCADE)
    name = models.CharField(max_length=40, verbose_name='活动名称')
    address = models.CharField(max_length=100, verbose_name='活动地址')
    lat = models.FloatField(verbose_name='维度')
    lon = models.FloatField(verbose_name='经度')
    time_detail = models.CharField(max_length=100, verbose_name='活动时间')
    introduction = models.CharField(max_length=200, verbose_name='内容简介')
    description = models.CharField(max_length=100, verbose_name='活动说明')
    detail = models.TextField(verbose_name='详细描述')
    total_quota = models.IntegerField(default=0, verbose_name='总名额')
    participant_num = models.IntegerField(default=0, verbose_name='报名名额')
    top_image = models.ImageField(max_length=250, verbose_name='顶部')
    image_list = models.TextField(verbose_name='图片列表')
    favor_num = models.IntegerField(default=0, verbose_name=u'点赞人数')

    created_time = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = u'商家活动啊'
        verbose_name_plural = u'商家活动'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        created = not self.id
        super(CommercialActivity, self).save(force_insert, force_update, using, update_fields)
        if created:
            from footprint.models import FlowType
            from footprint.manager.footprint_manager import add_to_flow
            add_to_flow(self.id, FlowType.ACTIVITY)


class ActivityParticipant(models.Model):
    # 活动参加者
    def __unicode__(self):
        return '{}__{}'.format(self.activity.name, self.user_info.nickname)
    activity = ForeignKey(CommercialActivity, on_delete=models.CASCADE, help_text='活动')
    user_info = ForeignKey(UserBaseInfo, on_delete=models.CASCADE, verbose_name='用户信息')
    name = models.CharField(max_length=40, verbose_name='标题')
    cellphone = models.CharField(max_length=20, verbose_name='标题')
    num = models.IntegerField(default=1, verbose_name='人数')
    hint = models.CharField(max_length=200, verbose_name=u'备注')


class TopBanner(models.Model):
    """
    顶部banner
    """
    def __unicode__(self):
        return '{}'.format(self.title)
    title = models.CharField(max_length=40, verbose_name='标题')
    image = models.CharField(max_length=250, verbose_name='图片啊')
    activity_id = models.PositiveIntegerField(verbose_name='活动id')
    is_online = models.BooleanField(default=False, verbose_name='是否上线')
    created_time = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)


class ExploreBanner(models.Model):
    """
    探索模式下的 Banner
    """
    def __unicode__(self):
        return '{title}_{id}'.format(title=self.title, id=self.id)

    class Meta:
        verbose_name = u'探索模式 Banner'
        verbose_name_plural = u'探索模式 Banner'

    title = models.CharField(max_length=40, verbose_name=u'标题')
    description = models.CharField(max_length=512, verbose_name=u'描述信息')
    image = models.CharField(max_length=250, verbose_name=u'图片啊')
    is_online = models.BooleanField(default=False, verbose_name=u'是否上线')
    created_time = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)


class ClubCouponTemplate(models.Model):
    """
    商家优惠券模板
    1. 优惠券名称：20字以内
    2. 优惠券类型：单选框
        1. 『普适券』
        2. 『满减券』
    3. 优惠券商家：选择框，需要精确到单个商家
    4. 优惠券金额：如果用户选择了『普适券』，隐藏即可
    5. 优惠券门槛：如果用户选择了『普适券』，隐藏即可
    6. 优惠券数量：0~9999自然数即可
    7. 上架和下架
    8. 优惠券到期日期
    """

    def __unicode__(self):
        return '{name}_{id}'.format(name=self.name, id=self.id)

    class Meta:
        verbose_name = u'商家优惠券模板'
        verbose_name_plural = u'商家优惠券模板'

    name = models.CharField(max_length=20, verbose_name=u'优惠券名称')
    template_type = models.CharField(choices=CouponTemplateChoices, verbose_name=u'优惠券类型', max_length=10)
    club = ForeignKey(Club, on_delete=models.CASCADE, verbose_name=u'商家')
    money = models.PositiveIntegerField(default=0, verbose_name=u'优惠券金额(对普适券不生效)')
    threshold = models.PositiveIntegerField(default=0, verbose_name=u'优惠券门槛(对普适券不生效)')
    count = models.PositiveIntegerField(default=0, verbose_name=u'优惠券数量')
    balance = models.PositiveIntegerField(default=0, verbose_name=u'优惠券余量')
    is_online = models.BooleanField(default=False, verbose_name=u'是否上线')
    deadline = models.DateTimeField(verbose_name=u'到期日期')

    created_time = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
