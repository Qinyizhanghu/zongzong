# -*- encoding:utf-8 -*-


import json

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from commercial.manager.club_user_manager import club_user_login
from commercial.manager.db_manager import get_club_user_info_by_user_info
from user_info.manager.user_info_mananger import get_user_info_by_user_id_db
from utilities.request_utils import get_data_from_request
from utilities.response import json_http_error, json_http_success
from weixin.manager.weixin_mini_manager import wx_mini_request_login, WxminiAuthManager


@csrf_exempt
@require_POST
def login_and_get_session_id_view(request):
    """
    使用小程序的登录然后返回session_id，目前支持两种登录方式：
    1、使用微信的code后台服务器验证方式
    2、使用春雨的用户名和账户验证
    URL[POST]: /weixin/get_session_id/
    :param request: {code, encryptedData, iv}
    """
    # 使用code方式进行登录
    post_data = get_data_from_request(request)
    code = post_data.get('code')
    encrypted_data = post_data.get('encryptedData')
    iv = post_data.get('iv')
    if code:
        user, session_key = WxminiAuthManager.sync_wx_mini_user_info(code, encrypted_data, iv)

    # 使用form表单携带账户和密码进行登录
    else:
        return json_http_error('缺少参数')

    # 用户登录返回session信息
    if not user:
        return json_http_error('invalid user')
    wx_mini_request_login(request, user, session_key)
    return json_http_success({"sessionid": request.session.session_key})


@csrf_exempt
@require_POST
def club_user_get_session_id_view(request):
    """
    商家用户使用 code 去换取 sessionid
    URL[POST]: /weixin/club/get_session_id/
    """
    post_data = get_data_from_request(request)
    code = post_data.get('code')

    if code:
        user, session_key = WxminiAuthManager.sync_wx_mini_user_info_for_club(code)
    else:
        return json_http_error('缺少参数')

    user_info = get_user_info_by_user_id_db(user.id)
    club_user_info = get_club_user_info_by_user_info(user_info)
    wx_mini_request_login(request, user, session_key)

    if not club_user_info.exists():
        return json_http_success({"sessionid": request.session.session_key})

    if club_user_info.count() > 1:
        return json_http_error(u'多用户商户错误')

    return json_http_success({'club_id': club_user_info[0].club.id, "sessionid": request.session.session_key})


@csrf_exempt
@require_POST
def club_user_login_view(request):
    """
    商家用户登录
    由于不需要商户的 "其他信息", 所以, 前端值传递 code 也是可以的
    URL[POST]: /weixin/club/login/
    """
    post_data = get_data_from_request(request)
    account = post_data['account']
    password = post_data['password']
    code = post_data.get('code')

    if code:
        user, session_key = WxminiAuthManager.sync_wx_mini_user_info_for_club(code)
    # 使用form表单携带账户和密码进行登录
    else:
        return json_http_error('缺少参数')

    # 如果之前这个用户登录过踪踪用户端, 那么, 这个 UserInfo 表对象也是有的
    user_info = get_user_info_by_user_id_db(user.id)
    user_extra_info = json.loads(user_info.extra_info)
    user_extra_info.update({'is_club': 1})
    user_info.extra_info = json.dumps(user_extra_info)
    user_info.save()

    club_user_info = club_user_login(account, password, user_info)

    if not club_user_info:
        return json_http_error(u'用户名或密码错误')

    wx_mini_request_login(request, user, session_key)
    return json_http_success({'club_id': club_user_info.club.id, "sessionid": request.session.session_key})
