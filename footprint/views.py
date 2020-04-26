import json
import logging

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from api.manager.positon_manager import add_user_location
from footprint.manager.comment_manager import create_comment_db
from footprint.manager.footprint_manager import create_footprint_db, add_favor_db, \
    build_footprint_detail, get_footprint_by_id_db, get_footprints_by_user_id_db, update_comment_num_db, \
    build_footprint_list_info
from footprint.models import FlowType
from user_info.manager.user_info_mananger import get_user_info_by_user_id_db
from utilities.content_check import is_content_valid
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
    footprint = create_footprint_db(request.user, content, latitude, longitude, location, image_list, hide)
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
    footprint_detail = build_footprint_detail(footprint, request.user.id)
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
