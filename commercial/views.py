import datetime

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from commercial.manager.banner_manager import get_top_banner_db, build_top_banner
from commercial.manager.activity_manager import build_club_info, \
    build_activity_detail, participate_activity, \
    build_activity_brief_info, get_nearby_clubs_info, build_club_activity_confirm_info, \
    club_confirm_activity_participant
from commercial.manager.club_user_manager import club_user_login, charge_off_user_coupon, \
    build_user_coupon_info_for_charge_off, build_club_consume_user_coupon_info, build_club_detail_info
from commercial.manager.db_manager import get_commercial_activity_by_id_db, get_commercial_activities_by_club_id_db, \
    get_club_by_id_db
from commercial.manager.explore_banner_manager import build_explore_banner, get_explore_banner_db, homepage_pop_up_info
from commercial.manager.explore_surplus_times_manager import ExploreSurplusTimesManager
from footprint.manager.footprint_manager import add_favor_db
from footprint.models import FlowType
from user_info.manager.user_info_mananger import get_user_info_by_user_id_db
from utilities.date_time import datetime_to_str, FORMAT_DATE_WITHOUT_SEPARATOR
from utilities.request_utils import get_page_range, get_data_from_request
from utilities.response import json_http_success, json_http_error


@require_GET
def get_top_banner_view(request):
    """
    获取顶部banner广告信息
    :return: {
        title, avatar,  activity_id,
    }
    """
    banner = get_top_banner_db()
    result = {} if not banner else build_top_banner(banner)
    return json_http_success(result)


@require_GET
def get_explore_banner_view(request):
    """
    获取顶部 explore banner 信息
    URL[GET]: /commercial/get_explore_banner/
    :return: {
        'title': banner.title,
        'description': banner.description,
        'image': banner.image
    }
    """
    return json_http_success(build_explore_banner(get_explore_banner_db()))


@require_GET
@login_required
def get_homepage_pop_up_view(request):
    """
    获取首次进入的探索模式弹框信息
    URL[GET]: /commercial/get_homepage_pop_up/
    :return: {
        'title': banner.title,
        'description': banner.description,
        'image': banner.image
    } or {}
    """
    return homepage_pop_up_info(get_user_info_by_user_id_db(request.user.id))


@require_GET
@login_required
def get_explore_surplus_times_view(request):
    """
    获取用户探索模式剩余的次数
    URL[GET]: /commercial/get_explore_surplus_times/
    :return int
    """
    user_info = get_user_info_by_user_id_db(request.user.id)
    current_date = datetime_to_str(datetime.datetime.now(), date_format=FORMAT_DATE_WITHOUT_SEPARATOR)

    surplus_times = ExploreSurplusTimesManager.get_explore_day_limit() \
        - ExploreSurplusTimesManager.get_times(current_date, user_info.id)

    return json_http_success({"surplus_times": surplus_times if surplus_times >= 0 else 0})


@require_GET
@login_required
def get_club_info_view(request):
    """
    获取俱乐部信息
    URL[GET]: /commercial/get_club_info/
    :param request:
    :return: {
        club_info: {
            id, name, avatar, address,
        }
        activities_info: [
            {
                activity_id, distance, title, created_time, activity_time, images_list,
                total_quota, participants: [
                    {
                        user_id, avatar
                    },
                ]
            },

        ]

    }
    """
    club_id = int(request.GET['club_id'])
    club = get_club_by_id_db(club_id)
    if not club:
        return json_http_error('id错误')
    club_info = build_club_info(club)
    return json_http_success(club_info)


@require_GET
@login_required
def activity_detail_view(request):
    """
    获取活动详细信息
    URL[GET]: /commercial/get_activity_detail/
    :return: {
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
    }
    """
    activity_id = request.GET['activity_id']
    activity = get_commercial_activity_by_id_db(activity_id)
    if not activity:
        return json_http_error('id错误')
    result = build_activity_detail(activity, request.user.id)
    return json_http_success(result)


@csrf_exempt
@require_POST
@login_required
def participate_activity_view(request):
    """
    用户报名活动
    URL[GET]: /commercial/subscribe_activity/
    """
    user = request.user
    post_data = get_data_from_request(request)
    activity_id = post_data['activity_id']
    name = post_data['name']
    cellphone = post_data['cellphone']
    num = int(post_data['num'])
    hint = post_data['hint']
    user_info = get_user_info_by_user_id_db(user.id)
    error_msg = participate_activity(activity_id, user_info.id, name, cellphone, num, hint)
    return json_http_success() if not error_msg else json_http_error(error_msg)


@require_GET
@login_required
def get_club_activities_info(request):
    """
    URL[GET]: /commercial/get_club_activity_info/
    :param request:
    :return:
    """
    club_id = int(request.GET['club_id'])
    page = int(request.GET.get('page', 1))
    lat = float(request.GET.get('lat', 0))
    lon = float(request.GET.get('lon', 0))
    start, end = get_page_range(page, 5)
    club = get_club_by_id_db(club_id)
    if not club:
        return json_http_error('错误')
    activities = get_commercial_activities_by_club_id_db(club_id, start, end)

    return json_http_success({'activity_list': [build_activity_brief_info(activity, request.user.id, lon, lat) for
                                                activity in activities],
                              'avatar': club.avatar})


@csrf_exempt
@require_POST
@login_required
def favor_activity_view(request):
    """
    给活动点赞
    URL[POST]: /commercial/favor_activity/
    :param request:
    :return:
    """
    post_data = get_data_from_request(request)
    activity_id = post_data['activity_id']
    favor_num = add_favor_db(activity_id, FlowType.ACTIVITY, request.user.id)
    return json_http_success({'favor_num': favor_num})


@require_GET
@login_required
def get_nearby_clubs_view(request):
    """
    获取用户 "附近的" 商家信息, 按照距离倒排
    URL[GET]: /commercial/nearby_clubs/
    """
    lon = float(request.GET.get('lon', 0))
    lat = float(request.GET.get('lat', 0))

    return json_http_success({'clubs': get_nearby_clubs_info(lon, lat)})


@csrf_exempt
@require_POST
@login_required
def club_user_login_view(request):
    """
    商家用户登录
    URL[POST]: /commercial/user_login/
    """
    post_data = get_data_from_request(request)
    account = post_data['account']
    password = post_data['password']

    user_info = get_user_info_by_user_id_db(request.user.id)

    club_user_info = club_user_login(account, password, user_info)
    if not club_user_info:
        return json_http_error(u'用户名或密码错误')
    return json_http_success({'club_id': club_user_info.club.id})


@require_GET
@login_required
def get_user_coupon_info_for_charge_off_view(request):
    """
    展示用户优惠券的信息 --> 用来核销的商户查看, 所以, 只会传递 coupon_code
    URL[GET]: /commercial/user_coupon_info_for_charge_off/
    """
    club_id = int(request.GET['club_id'])
    coupon_code = request.GET['coupon_code']

    coupon_info = build_user_coupon_info_for_charge_off(club_id, coupon_code)
    if not coupon_info:
        return json_http_error(u'优惠券码错误')
    return json_http_success(coupon_info)


@csrf_exempt
@require_POST
@login_required
def club_charge_off_user_coupon_view(request):
    """
    商家核销用户优惠券
    URL[POST]: /commercial/club_charge_off/
    """
    post_data = get_data_from_request(request)
    coupon_code = post_data['coupon_code']
    club_id = post_data['club_id']

    user_info = get_user_info_by_user_id_db(request.user.id)

    charge_off_result = charge_off_user_coupon(coupon_code, club_id, user_info)
    if not charge_off_result:
        return json_http_success({'club_id': club_id})
    return json_http_error(charge_off_result)


@require_GET
@login_required
def club_consume_user_coupon_info_view(request):
    """
    商户消耗用户优惠券详情
    URL[GET]: /commercial/consume_user_coupon_info/
    """
    club_id = int(request.GET['club_id'])
    consume_result = build_club_consume_user_coupon_info(club_id)
    if not consume_result:
        return json_http_error(u'找不到商家信息')
    return json_http_success(consume_result)


@require_GET
@login_required
def club_activity_confirm_info_view(request):
    """
    商户活动预约确认/未确认信息详情
    URL[GET]: /commercial/activity_confirm_info/
    """
    club_id = int(request.GET['club_id'])
    is_confirm = bool(int(request.GET['is_confirm']))   # 0-未确认; 1-已确认

    confirm_info = build_club_activity_confirm_info(club_id, is_confirm)
    if not confirm_info:
        return json_http_error(u'找不到商家信息')
    return json_http_success(confirm_info)


@csrf_exempt
@require_POST
@login_required
def club_confirm_activity_participant_view(request):
    """
    商户确认用户的活动预约
    URL[POST]: /commercial/confirm_activity_participant/
    """
    post_data = get_data_from_request(request)
    activity_participant_id = post_data['activity_participant_id']

    confirm_info = club_confirm_activity_participant(activity_participant_id)
    if confirm_info:
        return json_http_error(confirm_info)
    return json_http_success({})


@require_GET
# @login_required
def get_club_detail_view(request):
    """
    商户查看自己的信息
    """
    return json_http_success(build_club_detail_info(int(request.GET['club_id'])))


@csrf_exempt
@require_POST
@login_required
def club_update_detail_view(request):
    """
    商户更新自己的头像信息
    """



