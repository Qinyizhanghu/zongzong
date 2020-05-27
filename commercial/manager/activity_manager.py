import datetime

from geopy.distance import geodesic

from commercial.const import CouponTemplateChoices
from commercial.manager.db_manager import get_commercial_activity_by_id_db, create_activity_participate_record_db, \
    get_club_by_ids_db, get_club_by_id_db, get_commercial_activities_by_club, \
    get_activity_participate_by_activity_and_confirm, get_activity_participate_by_id
from commercial.models import CommercialActivity, ActivityParticipant, ClubCouponTemplate
from footprint.manager.footprint_manager import is_user_favored
from footprint.models import FlowType
from utilities.date_time import datetime_to_str
from utilities.distance_utils import haversine
from utilities.time_utils import get_time_show


def get_nearby_clubs_info(lon, lat):
    """
    获取用户附近的商家信息
    需要注意: 选择的是有优惠券模板配置的商家, 否则, 没有意义
    """
    coupon_templates = ClubCouponTemplate.objects.filter(is_online=True, balance__gt=0,
                                                         deadline__gt=datetime.datetime.now())
    if not coupon_templates:
        return {}

    club_id_set = set([template.club_id for template in coupon_templates])
    clubs = get_club_by_ids_db(club_id_set)
    club_infos = [build_nearby_club_info(club, lon, lat) for club in clubs]

    # 按照距离从近到远去展示出来
    club_infos.sort(key=lambda info: info['distance'])
    return club_infos


def build_nearby_club_info(club, lon, lat):
    """
    构造附近的商家信息
    """
    return {
        "club_id": club.id,
        "name": club.name,
        "address": club.address,
        "avatar": club.avatar,
        "distance": haversine(lon, lat, club.lon, club.lat),
        'lon': club.lon,
        'lat': club.lat
    }


def get_template_id_by_club(club):
    """
    根据商家去获取商家优惠力度最大的优惠券
    """
    templates = ClubCouponTemplate.objects.filter(is_online=True, balance__gt=0, deadline__gt=datetime.datetime.now(),
                                                  club=club)
    if not templates:
        return 0

    template_id_2_money = {}

    for template in templates:
        if template.template_type == CouponTemplateChoices.FULL:
            template_id_2_money[template.id] = template.money

    # 如果不存在满减券, 随机返回一个普适券
    if not template_id_2_money:
        return templates[0].id

    # 获取优惠力度最大的优惠券的 id
    return max(zip(template_id_2_money.values(), template_id_2_money.keys()))[1].id


def build_club_info(club):
    return {
        'avatar': club.avatar,
        'name': club.name,
        'address': club.address,
        'telephone': club.telephone,
        'club_id': club.id,
    }


def build_activity_info(activity, avatar):
    return {
        'activity_id': activity.id,
        'avatar': avatar,
        'title': activity.title,
        'post_time': activity.time_detail,
        'image_list': activity.image_list,
        'distance': 1,
    }


def get_club_activities_info(club_id, start_num, end_num):
    activities = CommercialActivity.objects.filter(club_id=club_id).order_by('-created_time')[start_num: end_num]
    if not activities:
        return {}
    avatar = activities[0].avatar
    return [build_activity_info(activity, avatar) for activity in activities]


def get_activity_participants(activity_id):
    return ActivityParticipant.objects.filter(activity_id=activity_id)


def build_activity_detail(activity, user_id):
    """
    构建活动详情页信息
            top_image,
        title,
        club_name,
        avatar,
        telephone,
        introduction,
        image_list,
        detail,
        address,
        time_detail,
        description,
        total_quota,
        participants: [{user_id, avatar}]
    """
    club = activity.club
    result = {
        'top_image': activity.top_image.url,
        'title': activity.name,
        'club_name': club.name,
        'avatar': club.avatar.url,
        'telephone': club.telephone,
        'introduction': activity.introduction,
        'detail': activity.detail,
        'address': activity.address,
        'time_detail': activity.time_detail,
        'description': activity.description,
        'total_quota': activity.total_quota,
        'image_list': activity.image_list,
        'favored': is_user_favored(user_id, activity.id, FlowType.ACTIVITY),
        'favor_num': activity.favor_num,
    }
    participants = get_activity_participants(activity.id)
    result.update({'participants': [{'user_id': item.user_info.user_id, 'avatar': item.user_info.avatar}
                                    for item in participants]})
    return result


def participate_activity(activity_id, user_info_id, name, cellphone, num, hint):
    activity = get_commercial_activity_by_id_db(activity_id)
    # 已经报名数 + 当前想要报名数
    if activity.participant_num + num > activity.total_quota:
        return '人数已满'
    record, created = create_activity_participate_record_db(activity_id, user_info_id, name, cellphone, num, hint)
    if not created:
        return u'请勿重复报名'

    # @zhanghu 用户的预约需要商户确认之后才增加报名人数, 这里只是记录用户预约, 不增加人数
    # activity.participant_num += num
    # activity.save()
    return ''


def build_activity_brief_info(activity, user_id, lon, lat):
    distance = geodesic((activity.lat, activity.lon), (lat, lon)).meters if lat and lon else 0
    return {
        'time_detail': activity.time_detail,
        'post_time': get_time_show(activity.created_time),
        'name': activity.name,
        'image_list': activity.image_list,
        'distance': distance,
        'activity_id': activity.id,
        'favored': is_user_favored(user_id, activity.id, FlowType.ACTIVITY),
        'favor_num': activity.favor_num
    }


def build_coupon_template_info(template):
    """
    构造优惠券模板信息
    商户 id、商户头像、商户名称、商户地址、优惠券名称、优惠券截止日期、优惠券金额
    """
    coupon_money = 0 if template.template_type == CouponTemplateChoices.GENERAL else template.money

    return {
        'club_id': template.club_id,
        'avatar': template.club.avatar,
        'club_name': template.club.name,
        'address': template.club.address,
        'template_id': template.id,
        'template_name': template.name,
        'deadline': datetime_to_str(template.deadline),
        'coupon_money': coupon_money,
        'type': 'coupon_template',
        'lon': template.club.lon,
        'lat': template.club.lat
    }


def build_club_activity_confirm_info(club_id, is_confirm):
    """
    构造商户活动预约确认信息
    """
    club = get_club_by_id_db(club_id)
    if not club:
        return None

    commercial_activities = get_commercial_activities_by_club(club)
    activity_participates = get_activity_participate_by_activity_and_confirm(commercial_activities, is_confirm)

    return {
        'club_info': {
            'avatar': club.avatar,
            'name': club.name,
            'address': club.address,
            'telephone': club.telephone,
            'club_id': club.id,
        },
        'activity_participant_info': [build_activity_participant_info(record) for record in activity_participates]
    }


def build_activity_participant_info(activity_participant):
    """
    构造用户预约信息
    """
    return {
        'activity_participant_id': activity_participant.id,
        'nickname': activity_participant.user_info.nickname,
        'activity_name': activity_participant.activity.name,
        'user_num': activity_participant.num,
        'time_detail': activity_participant.activity.time_detail,
        'participant_num': activity_participant.activity.participant_num,
        'total_quota': activity_participant.activity.total_quota
    }


def club_confirm_activity_participant(activity_participant_id):
    """
    商户确认用户预约
    """
    activity_participant = get_activity_participate_by_id(activity_participant_id)
    if not activity_participant_id:
        return u'找不到预约活动'

    if activity_participant.activity.participant_num + activity_participant.num \
            > activity_participant.activity.total_quota:
        return u'预约人数已满'

    activity_participant.is_confirm = True
    activity_participant.save()

    activity_participant.activity.participant_num += activity_participant.num
    activity_participant.activity.save()

    return u''
