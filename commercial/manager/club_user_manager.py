# -*- encoding:utf-8 -*-


"""
商家用户相关
"""


import logging

from commercial.manager.db_manager import get_club_by_account_and_password, create_club_user_info_by_user_info_and_club, \
    get_club_by_id_db, get_club_user_info_by_user_info_and_club
from commercial.models import CouponChargeOffRecord
from footprint.manager.coupon_manager import get_user_coupon_by_coupon_code, charge_off_coupon


def club_user_login(account, password, user_info):
    """
    商家用户登录, 如果没有直接创建
    """
    club = get_club_by_account_and_password(account, password)
    if not club:
        return None
    club_user_info, created = create_club_user_info_by_user_info_and_club(user_info, club)
    if created:
        logging.info('create ClubUserInfo: %s, %s', club.id, user_info.id)

    return club_user_info


def charge_off_user_coupon(coupon_code, club_id, user_info):
    """
    核销用户优惠券
    """
    user_coupon = get_user_coupon_by_coupon_code(coupon_code)

    # 如果根据优惠券码找不到优惠券, 返回 -1
    if not user_coupon:
        return u'找不到对应的优惠券'

    # 如果优惠券已经被核销了, 返回 -2
    if user_coupon.is_used:
        return u'优惠券已经被核销了'

    club = get_club_by_id_db(club_id)
    if not club:
        return u'俱乐部不存在'

    club_user_info = get_club_user_info_by_user_info_and_club(user_info, club)
    if not club_user_info:
        return u'商户账号不存在'

    coupon_charge_off_record = CouponChargeOffRecord.objects.create(
        club_user=club_user_info, coupon=user_coupon
    )
    charge_off_coupon(user_coupon)  # 除了记录之外, 还需要核销优惠券自身
    logging.info('charge off user coupon: %s, %s, %s', club.id, user_coupon.id, coupon_charge_off_record.id)

    return u''
