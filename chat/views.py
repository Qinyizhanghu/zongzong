import json

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from chat.manager.chat_manager import get_conversation_id_by_user_ids, create_chat_record_db, build_conversation_list, \
    get_or_create_conversation_info, get_conversation_info_by_conversation_id, get_conversation_info_by_user_ids
from chat.manager.message_manager import ConversationMessageManager
from utilities.content_check import is_content_valid
from utilities.image_check import is_image_valid
from utilities.request_utils import get_data_from_request
from utilities.response import json_http_success, json_http_error


@require_GET
@login_required
def get_my_conversation_list_view(request):
    """
    获取我的对话列表
    URL[GET]: /chat/conversation_list/
    :return: {
        "conversation_list": [
            {
                "avatar": "",
                "last_message": "",
                "has_new": "",
                "username": "",
                "conversation_id": ""
            }
        ]
    }
    """
    my_conversation_info_list = ConversationMessageManager.get_all_message_list(request.user.id)
    return json_http_success({'conversation_list': my_conversation_info_list})


@csrf_exempt
@require_POST
@login_required
def post_content_view(request):
    """
    发送信息
    URL[POST]: /chat/post_content/
    :param request: conversation_id， content_type， content
    """
    data = get_data_from_request(request)
    receiver_id = int(data.get('receiver_id'))
    conversation_id = data.get('conversation_id')
    if not receiver_id and not conversation_id:
        return json_http_error('参数错误')
    # 生成一个会话 id
    conversation_id = conversation_id or get_conversation_id_by_user_ids([receiver_id, request.user.id])
    content = data['content_json']
    if content['type'] == 'image':
        if not is_image_valid(content['url']):
            return json_http_error('请文明发言！')
    elif content['type'] == 'text':
        if not is_content_valid(content['text']):
            return json_http_error('请文明发言！')
    content_str = json.dumps(content)
    # 创建一条会话记录
    chat_record = create_chat_record_db(conversation_id, content_str, request.user.id)
    # 发推送、更新badge
    ConversationMessageManager.add_message(receiver_id, request.user.id, conversation_id, content)
    return json_http_success()


@csrf_exempt
@require_POST
@login_required
def explore_say_hello_view(request):
    """
    探索模式下的打招呼按钮
    URL[POST]: /chat/explore_say_hello/
    """
    data = get_data_from_request(request)
    receiver_id = int(data.get('receiver_id'))  # 消息接收者 id

    # 需要先根据 user_id 和 receiver_id 确定会话是否已经建立了
    user_ids = [int(receiver_id), request.user.id]
    user_ids.sort(key=lambda peer_id: int(peer_id))

    content = {
        'type': 'text',
        'text': [{"node": "text", "text": u"我来打个招呼~"}]
    }
    content_str = json.dumps(content)

    # 尝试获取会话信息
    chat_info = get_conversation_info_by_user_ids(user_ids[0], user_ids[1])
    # 如果获取不到, 则主动创建一个
    if not chat_info:
        conversation_id = get_conversation_id_by_user_ids([user_ids[0], user_ids[1]])
        chat_info, _ = get_or_create_conversation_info(conversation_id, user_ids[0], user_ids[1])

    # 创建一条会话记录
    chat_record = create_chat_record_db(chat_info.conversation_id, content_str, request.user.id)
    # 发推送、更新badge
    ConversationMessageManager.add_message(receiver_id, request.user.id, chat_info.conversation_id, content)

    return json_http_success()


@require_GET
@login_required
def get_conversation_detail_view(request):
    """
    获取聊天详情
    :param request:
    :return:
    """
    conversation_id = request.GET.get('conversation_id')
    receiver_id = request.GET.get('receiver_id')
    msg_id = int(request.GET.get('msg_id', 0))
    get_new = int(request.GET.get('get_new', 0))
    if conversation_id:
        conversation_info = get_conversation_info_by_conversation_id(conversation_id)
    elif receiver_id:
        conversation_id = get_conversation_id_by_user_ids([int(receiver_id), request.user.id])
        # 创建一个会话 id 记录, 对于用户 id 的存储, 第一个id < 第二个 id
        conversation_info, _ = get_or_create_conversation_info(conversation_id, request.user.id, int(receiver_id))
    else:
        return json_http_error('参数错误')
    result = build_conversation_list(request.user.id, conversation_id, conversation_info, msg_id, get_new)
    # 清除 badge
    ConversationMessageManager.clear_badge(request.user.id, conversation_id)
    return json_http_success(result)
