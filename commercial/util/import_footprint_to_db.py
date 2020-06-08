# -*- coding:utf8 -*-


"""
导入数据到足迹表中
1. fake User 和 BaseUserInfo
2. 录入 footprint
"""


import json
import os
import random

from commercial.util.stage_1_user_data import read_excel_for_stage_one_user_data, read_excel_for_stage_one_user, \
    random_lat_and_lon
from footprint.manager.footprint_manager import create_footprint_db
from footprint.models import PostType
from user_info.consts import SexChoices
from user_info.manager.user_info_mananger import get_or_create_user_db
from user_info.models import UserBaseInfo


class ImportFootprintToDB(object):
    """
    导入数据到足迹表中
    """
    @classmethod
    def acquire_image_dict_from_local(cls):
        """
        从本地获取到图片文件字典
        :return:
        """
        https_for_image = 'https://zongz.cn/media/img_cut/'
        image_dir = '/root/workspace/upload/img_cut/'
        img_list = []
        for i, j, k in os.walk(image_dir):
            img_list = k

        image_dict = {}

        for img_ in img_list:
            fake_id = img_.split('_')[0]
            if int(fake_id) not in image_dict:
                image_dict[int(fake_id)] = [https_for_image + img_]
            else:
                image_dict[int(fake_id)].append(https_for_image + img_)

        return image_dict

    @classmethod
    def build_footprint_dict_from_excel(cls, excel_path='/root/workspace/excel/stage_1_user_data.xlsx'):
        """
        构造足迹字典
        :return:
        """
        user_footprint_data = read_excel_for_stage_one_user_data(excel_path)
        print('current excel has footprint count: %s' % len(user_footprint_data))

        user_footprint_map = {}
        for user_footprint in user_footprint_data:
            username = user_footprint.name
            if username in user_footprint_map:
                user_footprint_map[username].append(user_footprint)
            else:
                user_footprint_map[username] = [user_footprint]

        return user_footprint_map

    @classmethod
    def build_user_data_from_excel(cls, excel_path='/root/workspace/excel/stage_1_user_data.xlsx'):
        """
        构造用户数据
        :param excel_path:
        :return:
        """
        user_data_dict = {'f': [], 'm': []}
        user_data = read_excel_for_stage_one_user(excel_path)

        for single_user in user_data:
            if single_user.gender == '男':
                user_data_dict['m'].append(single_user)
            else:
                user_data_dict['f'].append(single_user)

        return user_data_dict

    @classmethod
    def fake_user_info_to_db(cls, excel_path='/root/workspace/excel/stage_1_user_data.xlsx'):
        """
        构造数据库用户信息
        :return:
        """
        image_dict = cls.acquire_image_dict_from_local()
        user_data_dict = cls.build_user_data_from_excel(excel_path)
        user_footprint_map = cls.build_footprint_dict_from_excel(excel_path)

        for username in user_footprint_map:
            random_user = None
            # 任意一个 footprint
            anyone = user_footprint_map[username][0]
            if anyone.gender == '男':
                random_user = user_data_dict['m'][random.randint(0, len(user_data_dict['m']) - 1)]
            else:
                random_user = user_data_dict['f'][random.randint(0, len(user_data_dict['f']) - 1)]

            user, created = get_or_create_user_db(random_user.open_id)

            if created:
                try:
                    user_info = UserBaseInfo.objects.create(
                        user=user, open_id=random_user.open_id,
                        nickname=username, avatar=random_user.avatar,
                        signature=random_user.signature,
                        sex=SexChoices.MALE if anyone.gender == '男' else SexChoices.FEMALE,
                        extra_info=json.dumps({'fake_user': 1})
                    )
                except Exception as e:
                    user_info = UserBaseInfo.objects.create(
                        user=user, open_id=random_user.open_id,
                        nickname=username, avatar=random_user.avatar,
                        signature='今天天气不错',
                        sex=SexChoices.MALE if anyone.gender == '男' else SexChoices.FEMALE,
                        extra_info=json.dumps({'fake_user': 1})
                    )
                    print('create userinfo has some error: %s' % e)

            for footprint in user_footprint_map[username]:
                # 这里最重要的工作是获取到 footprint 对应的 image_list, 且最多9张
                image_list = []
                if int(footprint.fake_id) in image_dict:
                    image_list = image_dict[int(footprint.fake_id)]
                if len(image_list) > 9:
                    image_list = image_list[0: 9]

                lat, lon = random_lat_and_lon()

                try:
                    create_footprint_db(
                        user.id, footprint.message, lat, lon, None, image_list, 0, PostType.NOTE, 0
                    )
                except Exception as e:
                    print('create footprint has some error: %s' % e)
