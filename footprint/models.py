import json

from django.contrib.auth.models import User
from django.db import models

from commercial.models import ClubCouponTemplate
from user_info.consts import SexChoices
from utilities.enum import EnumBase, EnumItem


class FlowType(EnumBase):
    ACTIVITY = EnumItem(0, '商业活动')
    FOOTPRINT = EnumItem(1, '足迹')


class PostType(EnumBase):
    NOTE = EnumItem('note', u'普通发布的文字')
    HELP = EnumItem('help', u'求助帖')


# 优惠券获取的方式
class CouponAcquireWay(EnumBase):
    DRAW = EnumItem('draw', u'自己领取')
    DONATE = EnumItem('donate', u'他人赠送')


class TotalFlow(models.Model):
    """
    footprint和activity的合集
    """
    flow_id = models.PositiveIntegerField(verbose_name='footprint or commercial_activity id')
    flow_type = models.SmallIntegerField(choices=FlowType)
    created_time = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)


class Footprint(models.Model):
    """
    姓名 性别  年龄  标签  时间 地点  距离
    求助帖同样是用户发布的足迹
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, verbose_name=u'姓名')
    avatar = models.CharField(max_length=300, verbose_name=u'头像', null=True, default=None)
    sex = models.CharField(choices=SexChoices, verbose_name=u'性别', max_length=10)
    lat = models.CharField(max_length=20, verbose_name=u'维度', null=True, blank=True)
    lon = models.CharField(max_length=20, verbose_name=u'经度', null=True, blank=True)
    location = models.CharField(max_length=50, verbose_name=u'地点', null=True, blank=True)
    content = models.CharField(max_length=200, verbose_name=u'痕迹内容')
    image_list_str = models.TextField(verbose_name=u'图片列表json')
    favor_num = models.PositiveIntegerField(default=0, verbose_name=u'点赞数')
    comment_num = models.PositiveIntegerField(default=0, verbose_name=u'评论数')
    forward_num = models.PositiveIntegerField(default=0, verbose_name=u'转发数')
    hide = models.BooleanField(default=False, verbose_name=u'是否只有自己能看到')
    # @zhanghu
    is_deleted = models.BooleanField(default=False, verbose_name=u'是否被删除')
    post_type = models.CharField(choices=PostType, verbose_name=u'帖子类型', default=PostType.NOTE, max_length=10)
    template_id = models.IntegerField(default=0, verbose_name=u'优惠券模板 id')  # 求助帖需要优惠券模板的信息

    created_time = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    @property
    def image_list(self):
        return json.loads(self.image_list_str) if self.image_list_str else []

    @image_list.setter
    def image_list(self, image_list):
        self.image_list_str = json.dumps(image_list)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        created = not self.id
        super(Footprint, self).save(force_insert, force_update, using, update_fields)
        if created:
            from footprint.manager.footprint_manager import add_to_flow
            add_to_flow(self.id, FlowType.FOOTPRINT)

    class Meta:
        verbose_name = u'足迹'
        verbose_name_plural = u'足迹'


class Comment(models.Model):
    """
    痕迹或活动的评论
    """
    flow_id = models.PositiveIntegerField(verbose_name='footprint or commercial_activity id')
    flow_type = models.SmallIntegerField(choices=FlowType)
    user_id = models.IntegerField(verbose_name=u'评论者user_id')
    name = models.CharField(max_length=50, default='', blank=True, null=True, help_text='评论者昵称')
    avatar = models.CharField(max_length=255, default='', blank=True, null=True, help_text='评论者头像')
    comment = models.TextField(verbose_name=u'评论内容')
    image_list = models.CharField(max_length=1000, default='[]', help_text=u'评论附带图片')

    is_deleted = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = u'评论'
        verbose_name_plural = u'评论'


class Favor(models.Model):
    """
    痕迹点赞记录
    """
    flow_id = models.PositiveIntegerField(verbose_name='footprint or commercial_activity id')
    flow_type = models.SmallIntegerField(choices=FlowType)
    user_id = models.IntegerField(verbose_name=u'评论者user_id')
    favored = models.BooleanField(verbose_name=u'是否点赞', default=True)
    test = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)


class FootprintFavor(models.Model):
    """
    痕迹点赞记录
    """
    footprint = models.ForeignKey(Footprint, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    favored = models.BooleanField(verbose_name=u'是否点赞', default=True)
    created_time = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)


class FootprintCommentFavor(models.Model):
    """
    痕迹评论的点赞
    """
    footprint = models.IntegerField(verbose_name=u'话题id')
    footprint_comment_id = models.IntegerField(verbose_name='话题评论id')
    user_id = models.IntegerField(verbose_name=u'评论者user_id')
    favored = models.BooleanField(verbose_name=u'是否点赞', default=True)
    created_time = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)


class UserCoupon(models.Model):
    """
    用户优惠券
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey(ClubCouponTemplate, on_delete=models.CASCADE)
    acquire_way = models.CharField(choices=CouponAcquireWay, verbose_name=u'获取方式',
                                   default=CouponAcquireWay.DRAW, max_length=10)
    donate_user_id = models.IntegerField(verbose_name=u'赠送者 user_id', default=0)
    coupon_code = models.CharField(max_length=100, default='', blank=True, null=True, help_text='优惠券码')
    is_used = models.BooleanField(verbose_name=u'是否已使用', default=False)

    created_time = models.DateTimeField(auto_now_add=True, db_index=True)
    last_modified = models.DateTimeField(auto_now=True)
