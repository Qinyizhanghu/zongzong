# -*- encoding:utf-8 -*-


"""
商家用户相关
"""


import logging

from commercial.manager.db_manager import get_club_by_account_and_password, create_club_user_info_by_user_info_and_club


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

    return club_user_info.id
