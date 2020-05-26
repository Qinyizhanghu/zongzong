# -*- encoding:utf-8 -*-


"""
商家用户相关
"""


import logging

from commercial.const import CouponTemplateChoices
from commercial.manager.db_manager import get_club_by_account_and_password, create_club_user_info_by_user_info_and_club, \
    get_club_by_id_db, get_club_user_info_by_user_info_and_club, get_club_user_info_by_club, \
    get_charge_off_record_by_club_user_infos
from commercial.models import CouponChargeOffRecord
from footprint.manager.coupon_manager import get_user_coupon_by_coupon_code, charge_off_coupon
from user_info.manager.user_info_mananger import get_user_info_by_user_id_db
from utilities.date_time import datetime_to_str


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


def build_user_coupon_info_for_charge_off(club_id, coupon_code):
    """
    构造用户优惠券信息 --> 核销展示使用
    """
    club = get_club_by_id_db(club_id)
    if not club:
        return None

    coupon = get_user_coupon_by_coupon_code(coupon_code)
    if not coupon:
        return None

    user_info = get_user_info_by_user_id_db(coupon.user.id)
    coupon_money = 0 if coupon.template.template_type == CouponTemplateChoices.GENERAL else coupon.template.money

    return {
        'club_info': {
            'avatar': club.avatar,
            'name': club.name,
            'address': club.address,
            'telephone': club.telephone,
            'club_id': club.id,
        },
        'coupon_info': {
            'coupon_id': coupon.id,
            'coupon_money': coupon_money,
            'coupon_type': coupon.template.template_type,
            'coupon_name': coupon.template.name,
            'coupon_deadline': datetime_to_str(coupon.template.deadline)
        },
        'user_info': {
            'avatar': user_info.avatar,
            'nickname': user_info.nickname,
            'consume_count': CouponChargeOffRecord.objects.filter(user_id=coupon.user.id).count()
        }
    }


def charge_off_user_coupon(coupon_code, club_id, user_info):
    """
    核销用户优惠券
    """
    user_coupon = get_user_coupon_by_coupon_code(coupon_code)

    if not user_coupon:
        return u'找不到对应的优惠券'

    if user_coupon.is_used:
        return u'优惠券已经被核销了'

    club = get_club_by_id_db(club_id)
    if not club:
        return u'俱乐部不存在'

    club_user_info = get_club_user_info_by_user_info_and_club(user_info, club)
    if not club_user_info:
        return u'商户账号不存在'

    coupon_charge_off_record = CouponChargeOffRecord.objects.create(
        club_user=club_user_info, coupon_id=user_coupon.id, user_id=user_coupon.user.id
    )
    charge_off_coupon(user_coupon)  # 除了记录之外, 还需要核销优惠券自身
    logging.info('charge off user coupon: %s, %s, %s', club.id, user_coupon.id, coupon_charge_off_record.id)

    return u''


def build_club_consume_user_coupon_info(club_id):
    """
    构造商户消耗用户优惠券详情
    """
    club = get_club_by_id_db(club_id)
    if not club:
        return None

    club_user_infos = get_club_user_info_by_club(club_id)
    charge_off_records = get_charge_off_record_by_club_user_infos(club_user_infos)
    money, consume_infos = build_club_consume_infos(charge_off_records)

    return {
        'club_info': {
            'avatar': club.avatar,
            'name': club.name,
            'address': club.address,
            'telephone': club.telephone,
            'club_id': club.id,
        },
        'consume_sum': {
            'count': len(consume_infos),
            'money': money
        },
        'consume_infos': consume_infos
    }


def build_club_consume_infos(charge_off_records):
    """
    构造商户消耗优惠券的信息
    """
    money = 0
    consume_infos = []

    for record in charge_off_records:
        coupon_money = 0 if record.coupon.template.template_type == CouponTemplateChoices.GENERAL \
            else record.coupon.template.money
        consume_infos.append(
            {
                'nickname': get_user_info_by_user_id_db(record.coupon.user_id).nickname,
                'coupon_money': coupon_money,
                'confirm_user': record.club_user.user_info.nickname,
                'confirm_time': datetime_to_str(record.created_time, '%m-%d %H:%M')
            }
        )
        money += coupon_money

    return money, consume_infos
