import datetime
import json
import logging

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from api.manager.positon_manager import add_user_location
from commercial.manager.activity_manager import get_template_id_by_club, build_coupon_template_info
from commercial.manager.db_manager import get_club_by_id_db, get_coupon_template_by_id_db
from commercial.manager.explore_surplus_times_manager import ExploreSurplusTimesManager
from footprint.manager.comment_manager import create_comment_db
from footprint.manager.coupon_manager import build_user_coupon_list_info, build_user_coupon_info, acquire_new_coupon, \
    get_user_coupon_count, get_user_coupon_by_template, delete_user_coupon_by_id
from footprint.manager.footprint_manager import create_footprint_db, add_favor_db, \
    build_footprint_detail, get_footprint_by_id_db, get_footprints_by_user_id_db, update_comment_num_db, \
    build_footprint_list_info
from footprint.manager.next_explore_post_manager import get_next_explore_template, get_next_explore_footprint, \
    build_footprint_info_for_explore
from footprint.models import FlowType, PostType, UserCoupon, CouponAcquireWay
from user_info.manager.user_info_mananger import get_user_info_by_user_id_db
from utilities.content_check import is_content_valid
from utilities.date_time import datetime_to_str, FORMAT_DATE_WITHOUT_SEPARATOR
from utilities.image_check import is_image_valid
from utilities.request_utils import get_data_from_request, get_page_range
from utilities.response import json_http_success, json_http_error


@csrf_exempt
@login_required
def add_favor_view(request):
    """
    点赞view,点击两次的话就取消了
    URL[POST]: /footprint/favor/
    :param request: footprint id
    :return favor_num: 总的点赞数
    """
    post_data = get_data_from_request(request)
    footprint_id = post_data['footprint_id']
    favor_num = add_favor_db(footprint_id, FlowType.FOOTPRINT, request.user.id)
    return json_http_success({'favor_num': favor_num})


@csrf_exempt
@login_required
def comment_footprint_view(request):
    """
    URL[POST]: /footprint/comment/
    评论footprint，目前只能评论主贴
    :param request:
    :return:
    """
    post_data = get_data_from_request(request)
    footprint_id = post_data['footprint_id']
    comment = post_data['comment']
    if not is_content_valid(comment):
        return json_http_error('请注意用词')
    success = create_comment_db(request.user, footprint_id, comment)
    if success:
        comment_num = update_comment_num_db(footprint_id)
        return json_http_success({'comment_num': comment_num})
    return json_http_error()


@csrf_exempt
@login_required
def post_footprint_view(request):
    """
    发布踪踪动态
    求助帖的发布与 V1 的帖子不同之处只有一点: 需要传递商家 id
    URL[POST]: /footprint/create/
    :param request:
    :return:
    """
    post_data = get_data_from_request(request)
    latitude = post_data.get('lat')
    longitude = post_data.get('lon')
    location = post_data.get('location')
    content = post_data['content']
    if content and not is_content_valid(content):
        return json_http_error('请注意用词')
    image_list = post_data['image_list']
    if isinstance(image_list, str):
        image_list = json.loads(image_list)
    for image in image_list:
        logging.info('{}{}'.format(image, type(image)))
        if not is_image_valid(image):
            return json_http_error('请文明发言')
    hide = bool(int(post_data.get('hide', 0)))

    # @zhanghu 在这里校验下是不是帮助贴
    club = get_club_by_id_db(int(post_data.get('club_id', 0)))
    if not club:
        footprint = create_footprint_db(request.user, content, latitude, longitude, location, image_list, hide,
                                        PostType.NOTE, 0)
    else:
        # 找到金额最大的优惠券模板, 或者是一个普适券(注意, 如果找不到优惠券, 仍然降级为 NOTE 类型的足迹)
        target_template_id = get_template_id_by_club(club)
        post_type = PostType.HELP if target_template_id > 0 else PostType.NOTE
        footprint = create_footprint_db(request.user, content, latitude, longitude, location, image_list, hide,
                                        post_type, target_template_id)

    if latitude and longitude:
        add_user_location(footprint.id, longitude, latitude)
    return json_http_success()


@login_required
def get_footprint_detail_view(request):
    """
    /footprint/detail/
    获取痕迹详情
    包含：
    1.footprint详情
    2.评论： 距离
    3.评论的点赞数
    :param request:
    :return:
    """
    footprint_id = request.GET.get('footprint_id')
    footprint = get_footprint_by_id_db(footprint_id)
    footprint_detail = build_footprint_detail(footprint, request.user)
    return json_http_success(footprint_detail)


@login_required
def get_user_footprint_track_view(request):
    """
    /footprint/user_track/
    :param request:
    :return:
    """
    user_id = int(request.GET.get('user_id', 0)) or request.user.id
    page = int(request.GET.get('page', 0))
    lat = float(request.GET.get('lat', 0))
    lon = float(request.GET.get('lon', 0))
    start, end = get_page_range(page, 5)
    footprints = get_footprints_by_user_id_db(user_id, start, end)
    has_more = len(footprints) > 5
    footprints = footprints[:5]
    result = build_footprint_list_info(footprints, request.user.id, lat, lon)
    return json_http_success({'footprints': result, 'has_more': has_more})


@login_required
def user_delete_footprint_view(request):
    """
    用户删除自己发表的足迹记录
    /footprint/user_delete/
    """
    user_id = int(request.GET.get('user_id', 0)) or request.user.id
    footprint_id = int(request.GET.get('footprint_id', 0))

    footprint = get_footprint_by_id_db(footprint_id)
    if not footprint or footprint.user_id != user_id:
        return json_http_success({})

    footprint.is_deleted = True
    footprint.save()
    return json_http_success({})


@login_required
def help_post_pop_up_view(request):
    """
    用户首次进入帮助贴的弹窗
    /footprint/user_help_post_pop_up/
    """
    user_info = get_user_info_by_user_id_db(request.user.id)
    user_info_extra = json.loads(user_info.extra_info)

    if 'first_time_help_post' not in user_info_extra:
        user_info_extra['first_time_help_post'] = True
        user_info.extra_info = json.dumps(user_info_extra)
        user_info.save()
        return json_http_success({
            "title": u'【掘地求胜】求助帖说明',
            "image": u'',
            "description": u'欢迎来到【掘地求胜】活动，在这里，如何您有中意的商家，'
                           u'您可以向周围的小哥哥/小姐姐发送求助，索要商家优惠券。\n您只要选择商家后，点击发布TA就能看到啦~'
        })

    return json_http_success({})


@require_GET
@login_required
def get_user_coupon_list_view(request):
    """
    获取用户优惠券列表信息
    /footprint/user_coupon_list/
    """
    return json_http_success({'coupons': build_user_coupon_list_info(request.user)})


@require_GET
@login_required
def get_user_coupon_info_view(request):
    """
    获取单张用户优惠券信息
    /footprint/user_coupon_info/
    """
    coupon_id = int(request.GET.get('coupon_id', 0))
    return json_http_success(build_user_coupon_info(UserCoupon.objects.get(id=coupon_id)))


@require_GET
@login_required
def get_next_explore_post_view(request):
    """
    获取信息流的下一个:
    1. 信息流包含: 普通信息(足迹, 求助帖) + 优惠券信息
    2. [3, 9, 20, 30] 这四个位置是优惠券, 如果没有足够的普通信息, 都填充优惠券就可以了
    3. 0~10km、10~30km、30~100km、100km 及以上

    GET: /footprint/next_explore_post/

    一共有四种返回类型: text, image_text, coupon_template, help
    """
    lon = float(request.GET.get('lon', 0))
    lat = float(request.GET.get('lat', 0))

    user_info = get_user_info_by_user_id_db(request.user.id)
    current_date = datetime_to_str(datetime.datetime.now(), date_format=FORMAT_DATE_WITHOUT_SEPARATOR)
    next_explore_times = int(ExploreSurplusTimesManager.get_times(current_date, user_info.id)) + 1

    if next_explore_times > ExploreSurplusTimesManager.EXPLORE_DAY_LIMIT:
        return json_http_error(u'今天的次数已经用完了')

    # 增加一次探索次数
    ExploreSurplusTimesManager.add_times(current_date, user_info.id)

    # 随机返回一张优惠券, 但是, 注意位置 (获取不到优惠券, 返回用户足迹吧)
    if next_explore_times in [3, 9, 20, 30]:
        coupon_template = get_next_explore_template(next_explore_times)
        if coupon_template:
            # 返回的信息里面带有 type, 前端识别不同的 type 去展示
            return json_http_success(build_coupon_template_info(coupon_template))
        else:
            footprint = get_next_explore_footprint(next_explore_times, lon, lat, request.user)
            if footprint:
                return json_http_success(build_footprint_info_for_explore(request.user, footprint))
            return json_http_error(u'没有更多的探索啦')
    else:
        # 如果不是优惠券的位置, 返回足迹
        footprint = get_next_explore_footprint(next_explore_times, lon, lat, request.user)
        if footprint:
            return json_http_success(build_footprint_info_for_explore(request.user, footprint))
        # 如果获取不到足迹, 再尝试返回优惠券
        coupon_template = get_next_explore_template(next_explore_times, ignore_index=True)
        if coupon_template:
            return json_http_success(build_coupon_template_info(coupon_template))
        # 如果优惠券也获取不到
        return json_http_error(u'没有更多的探索啦')


@csrf_exempt
@require_POST
@login_required
def acquire_coupon_template_view(request):
    """
    用户主动领取优惠券模板
    POST: /footprint/acquire_coupon/
    """
    user = request.user
    post_data = get_data_from_request(request)

    template = get_coupon_template_by_id_db(post_data['template_id'])
    return json_http_success({'id': acquire_new_coupon(user, template)})


@csrf_exempt
@require_POST
@login_required
def donate_coupon_to_others_view(request):
    """
    用户把自己的优惠券转赠给其他人
    POST: /footprint/donate_coupon/
    """
    user = request.user
    post_data = get_data_from_request(request)
    # 转赠的目标用户
    target_user = get_user_info_by_user_id_db(post_data['user_id']).user

    template = get_coupon_template_by_id_db(post_data['template_id'])
    if get_user_coupon_count(user, template) <= 0:
        return json_http_error(u'您当前没有该商家优惠券~优惠券在信息流中获取哦~')

    user_coupon = get_user_coupon_by_template(user, template)[0]
    acquire_new_coupon(target_user, template, acquire_way=CouponAcquireWay.DONATE,
                       donate_user_id=user.id, coupon_code=user_coupon.coupon_code)
    delete_user_coupon_by_id(user_coupon.id)

    return json_http_success({})
