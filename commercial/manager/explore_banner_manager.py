# -*- encoding:utf-8 -*-


"""
探索模式下的 Banner 管理
"""
import json

from commercial.models import ExploreBanner


def get_explore_banner_db():
    """
    找到最新的一个探索模式 Banner
    """
    top_banner = ExploreBanner.objects.filter(is_online=True).order_by('-last_modified')[:1]
    return top_banner[0] if top_banner else None


def build_explore_banner(banner):
    """
    构造探索模式 Banner 详情信息
    """
    if not banner:
        return {}

    return {
        'title': banner.title,
        'description': banner.description,
        'image': banner.image
    }


def homepage_pop_up_info(user_info):
    """
    获取首页弹窗的信息
    这个只有用户首次进入小程序的时候才会弹出, 信息记录在 UserInfo 的 extra 字段中
    """
    user_info_extra = json.loads(user_info.extra_info)

    if 'first_time_explore' not in user_info_extra:
        user_info_extra['first_time_explore'] = True
        user_info.extra_info = json.dumps(user_info_extra)
        user_info.save()
        return build_explore_banner(get_explore_banner_db())

    return {}
