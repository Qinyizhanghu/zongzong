# -*- coding:utf-8 -*-


"""
用户优惠券管理模块
"""
from commercial.const import CouponTemplateChoices
from footprint.models import CouponAcquireWay, UserCoupon
from redis_utils.container.api_redis_client import redis
from user_info.manager.user_info_mananger import get_user_info_by_user_id_db
from utilities.date_time import datetime_to_str
from utilities.string_utils import random_numerical


class UserNewCouponManager(object):
    """
    用户是否有新的优惠券 cache 管理
    """

    @classmethod
    def build_redis_key(cls):
        """
        cache key
        """
        return "zongzong_user_new_coupon_info"

    @classmethod
    def get_new_coupon(cls, user_info_id):
        new_coupon_info = redis.hget_pickle(cls.build_redis_key(), user_info_id)
        if not new_coupon_info:
            return False
        return bool(new_coupon_info['has_new'])

    @classmethod
    def set_new_coupon(cls, user_info_id):
        new_coupon_info = redis.hget_pickle(cls.build_redis_key(), user_info_id)
        if not new_coupon_info:
            redis.hset_pickle(cls.build_redis_key(), user_info_id, {"has_new": 1})
            return
        else:
            new_coupon_info['has_new'] = 1
            redis.hset_pickle(cls.build_redis_key(), user_info_id, new_coupon_info)

    @classmethod
    def cancel_new_coupon(cls, user_info_id):
        new_coupon_info = redis.hget_pickle(cls.build_redis_key(), user_info_id)
        if not new_coupon_info:
            redis.hset_pickle(cls.build_redis_key(), user_info_id, {"has_new": 0})
            return
        else:
            new_coupon_info['has_new'] = 0
            redis.hset_pickle(cls.build_redis_key(), user_info_id, new_coupon_info)


def acquire_new_coupon(user, template, acquire_way=CouponAcquireWay.DRAW, donate_user_id=0, coupon_code=None):
    """
    获取新的优惠券
    """
    coupon = UserCoupon.objects.create(
        user=user,
        template=template,
        acquire_way=acquire_way,
        donate_user_id=donate_user_id,
        coupon_code=coupon_code if coupon_code else random_numerical(),
        is_used=False
    )

    # 获取了新的优惠券之后, 更新缓存信息
    user_info = get_user_info_by_user_id_db(user.id)
    UserNewCouponManager.set_new_coupon(user_info.id)

    return coupon.id


def build_user_coupon_list_info(user):
    """
    构造用户优惠券信息列表
    """
    coupons = UserCoupon.objects.filter(user=user).order_by('-created_time')

    # 打开优惠券信息列表, 更新缓存信息
    user_info = get_user_info_by_user_id_db(user.id)
    UserNewCouponManager.cancel_new_coupon(user_info.id)

    return [build_user_coupon_info(coupon) for coupon in coupons]


def build_user_coupon_info(coupon):
    """
    构造单个用户优惠券信息:
        商家头像
        商家名称
        优惠券金额
        优惠券名称
        优惠券到期日期
    """

    coupon_money = u'礼品券' if coupon.template.template_type == CouponTemplateChoices.GENERAL \
        else str(coupon.template.money)

    return {
        'club_id': coupon.template.club.id,
        'avatar': coupon.template.club.avatar,
        'club_name': coupon.template.club.name,
        'coupon_id': coupon.id,
        'coupon_money': coupon_money,
        'coupon_type': coupon.template.template_type,
        'coupon_name': coupon.template.name,
        'coupon_deadline': datetime_to_str(coupon.template.deadline),
        'coupon_is_used': coupon.is_used
    }
