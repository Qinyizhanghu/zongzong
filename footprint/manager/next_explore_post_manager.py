# -*- coding:utf-8 -*-


"""
获取信息流的下一个
"""
import datetime
import random

from api.manager.positon_manager import user_location_container
from commercial.models import ClubCouponTemplate
from footprint.manager.footprint_manager import get_footprints_by_ids_db

NEXT_EXPLORE_TEMPLATE_MAP = {
    3: 1,
    9: 2,
    20: 3,
    30: 4,
}


def get_next_explore_template(next_explore_times, ignore_index=False):
    """
    获取信息流下一个优惠券模板(支持用户领取同样的优惠券)
    :param next_explore_times: 下一个信息流的位置
    :param ignore_index: 忽略索引
    """
    coupon_templates = ClubCouponTemplate.objects.filter(is_online=True, balance__gt=0,
                                                         deadline__gt=datetime.datetime.now()).order_by('-created_time')
    if len(coupon_templates) == 0:
        return None

    if ignore_index:
        return coupon_templates[random.randint(0, len(coupon_templates) - 1)]

    next_explore_template_index = NEXT_EXPLORE_TEMPLATE_MAP.get(next_explore_times)
    # 如果优惠券个数较少, 随便返回一个
    if len(coupon_templates) < next_explore_template_index:
        return coupon_templates[random.randint(0, len(coupon_templates) - 1)]

    return coupon_templates[next_explore_template_index - 1]


def get_next_explore_footprint(next_explore_times, lon, lat, user):
    """
    获取信息流下一个用户足迹
    0~10km、10~30km、30~100km、100km 及以上
    """
    user_locations_10 = user_location_container.get_members_within_radius(lon, lat, 10)
    footprints_10 = get_footprints_by_ids_db([int(item) for item in user_locations_10])
    footprints_10_ids = [footprint.id for footprint in footprints_10]

    legal_footprints_10 = []
    for footprints_x in footprints_10:
        if footprints_x.user != user:
            legal_footprints_10.append(footprints_x)

    if len(legal_footprints_10) >= next_explore_times:
        return legal_footprints_10[next_explore_times - 1]

    # 这里获取的是 0 ~ 30 KM 以内的, 所以, 需要去掉 user_locations_10
    user_locations_30 = user_location_container.get_members_within_radius(lon, lat, 30)
    footprints_30 = get_footprints_by_ids_db([int(item) for item in user_locations_30])
    footprints_30_ids = [footprint.id for footprint in footprints_30]

    legal_footprints_30 = []
    for footprints_y in footprints_30:
        if footprints_y.user != user and footprints_y.id not in footprints_10_ids:
            legal_footprints_30.append(footprints_y)

    if len(legal_footprints_10) + len(legal_footprints_30) >= next_explore_times:
        return legal_footprints_30[next_explore_times - len(legal_footprints_10) - 1]

    # 这里获取的是 30 ~ 100 KM 以内的, 所以, 需要去掉 user_locations_30
    user_locations_100 = user_location_container.get_members_within_radius(lon, lat, 100)
    footprints_100 = get_footprints_by_ids_db([int(item) for item in user_locations_100])
    footprints_100_ids = [footprint.id for footprint in footprints_100]

    legal_footprints_100 = []
    for footprints_z in footprints_100:
        if footprints_z.user != user and footprints_z.id not in footprints_30_ids:
            legal_footprints_100.append(footprints_z)

    if len(legal_footprints_10) + len(legal_footprints_30) + len(legal_footprints_100) >= next_explore_times:
        return legal_footprints_100[next_explore_times - len(legal_footprints_30) - len(legal_footprints_10) - 1]

    # 100KM 以内都不满足的话, 那就获取 2000 公里以内的
    user_locations_2000 = user_location_container.get_members_within_radius(lon, lat, 2000)
    footprints_2000 = get_footprints_by_ids_db([int(item) for item in user_locations_2000])

    legal_footprints_2000 = []
    for footprints_xyz in footprints_2000:
        if footprints_xyz.user != user and footprints_xyz.id not in footprints_100_ids:
            legal_footprints_2000.append(footprints_xyz)

    if len(legal_footprints_10) + len(legal_footprints_30) + len(legal_footprints_100) + len(legal_footprints_2000) \
            >= next_explore_times:
        return legal_footprints_2000[next_explore_times - len(legal_footprints_100) - len(legal_footprints_30)
                                     - len(legal_footprints_10) - 1]

    # 实在是获取不到就返回 None
    return None
