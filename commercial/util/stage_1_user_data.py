# -*- coding:utf8 -*-


"""
将第一阶段用户数据文件导入到数据库表中
"""


import random

import xlrd

from utilities.date_time import str_to_datetime, FORMAT_DATETIME


class StageOneUser(object):

    def __init__(self, gender, avatar, signature, open_id):
        self.gender = gender
        self.avatar = avatar
        self.signature = signature
        self.open_id = open_id

    def __str__(self):
        return '%s-%s-%s' % (self.gender, self.avatar, self.signature)


class StageOneUserData(object):

    def __init__(self, name, gender, post_date, message, image_list, fake_id):
        self.name = name
        self.gender = gender
        self.post_date = post_date
        self.message = message
        self.image_list = image_list

        self.fake_id = fake_id

    def __str__(self):
        return '%s-%s-%s -> %d -> %s' % (self.name, self.gender, self.post_date, len(self.image_list), self.image_list)


def read_excel_for_stage_one_user(excel_path='/root/workspace/excel/users.xlsx'):
    user_data = []

    excel_object = xlrd.open_workbook(excel_path)
    table = excel_object.sheets()[1]

    nrows = table.nrows  # 行数
    ncole = table.ncols  # 列数

    fake_open_id = 1

    for i in range(0, nrows):
        row_values = table.row_values(i)
        gender = row_values[0]
        avatar = row_values[1]
        signature = row_values[2]

        user_data.append(StageOneUser(gender, avatar, signature, fake_open_id))
        fake_open_id += 1

    return user_data


def read_excel_for_stage_one_user_data(excel_path='/root/workspace/excel/users.xlsx'):
    """
    读 excel 文件
    注意: 到时候写入 fake user 的时候, 在 BaseUserInfo 的 extra_info 里面记录下这是个 fake 的 user --> 先检查下有没有执行过
    :param excel_path:
    :return:
    """
    user_data = []

    excel_object = xlrd.open_workbook(excel_path)
    table = excel_object.sheets()[0]

    nrows = table.nrows  # 行数
    ncole = table.ncols  # 列数

    fake_id = 1

    for i in range(1, nrows):
        row_values = table.row_values(i)
        name = row_values[1]
        gender = row_values[2]
        message = row_values[4]
        try:
            post_date = str_to_datetime(post_date_filling(row_values[3]), FORMAT_DATETIME)
        except IndexError:
            continue

        image_list = []
        for j in range(5, len(row_values)):
            if not row_values[j]:
                continue
            image_list_ = row_values[j].split(',')
            image_list.extend(image_list_)

        user_data.append(StageOneUserData(name, gender, post_date, message, image_list, fake_id))
        fake_id += 1
        # print(user_data[-1])

    return user_data


def post_date_filling(post_date):
    """
    填充帖子发布的时间
    :param post_date:
    :return:
    """
    post_date = post_date.lstrip()
    if '月' in post_date:
        post_date = '2020-' + post_date.replace('月', '-').replace('日', '')

    date_and_time = post_date.split(' ')
    date_split = date_and_time[0].split('-')
    month = date_split[1] if len(date_split[1]) == 2 else '0' + date_split[1]
    day = date_split[2] if len(date_split[2]) == 2 else '0' + date_split[2]
    second_filling = date_split[0] + '-' + month + '-' + day + ' ' + date_and_time[1] + ':00'

    return second_filling


def random_lat_and_lon():
    """
    随机的经纬度
    :return:
    """
    lat_range = [39.26, 41.03]
    lon_range = [115.25, 117.30]

    return random.uniform(lat_range[0], lat_range[1]), random.uniform(lon_range[0], lon_range[1])


# read_excel_for_stage_one_user_data('/Users/zhanghu05/QinyiZhang/zongzong/stage_1_user_data.xlsx')
# read_excel_for_stage_one_user('/Users/zhanghu05/QinyiZhang/zongzong/stage_1_user_data.xlsx')
