# -*- encoding:utf-8 -*-


"""
探索模式剩余次数管理
每个用户每天有 30次 探索的机会
"""

from redis_utils.container.api_redis_client import redis


class ExploreSurplusTimesManager(object):
    """
    探索模式剩余次数管理
    """
    EXPLORE_DAY_LIMIT = 30
    EXPIRE_TIME = 60 * 60 * 24 * 2  # 过期时间为 2 天

    @classmethod
    def get_explore_day_limit(cls):
        return cls.EXPLORE_DAY_LIMIT

    @classmethod
    def build_redis_key(cls, current_date):
        """
        这里的 key 一定要带着时间
        """
        return "explore_surplus_times_{}".format(current_date)

    @classmethod
    def add_times(cls, current_date, user_info_id, times=1):
        """
        增加探索模式的次数
        """
        new_times_info = {}
        old_times_info = cls.get_raw_times(current_date, user_info_id)
        if not old_times_info:
            new_times_info['times'] = times
        else:
            old_times_info['times'] = old_times_info['times'] + times
            new_times_info = old_times_info

        redis.hset_pickle(cls.build_redis_key(current_date), user_info_id, new_times_info)
        redis.expire(cls.build_redis_key(current_date), cls.EXPIRE_TIME)

    @classmethod
    def get_raw_times(cls, current_date, user_info_id):
        times_info = redis.hget_pickle(cls.build_redis_key(current_date), user_info_id)
        if not times_info:
            return {}

        return times_info

    @classmethod
    def get_times(cls, current_date, user_info_id):
        times_info = redis.hget_pickle(cls.build_redis_key(current_date), user_info_id)
        if not times_info:
            return 0

        return times_info['times']
