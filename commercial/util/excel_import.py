# -*- coding:utf8 -*-


"""
将 excel 文件导入到数据库表中
"""


import xlrd


class FakeUser(object):

    def __init__(self, name, gender, avatar, location, follower, fans, weibo, intro, tag, education, career, open_id):
        self.name = name
        self.gender = gender
        self.avatar = avatar
        self.location = location
        self.follower = follower
        self.fans = fans
        self.weibo = weibo
        self.intro = intro
        self.tag = tag
        self.education = education
        self.career = career

        # fake 一个 openid 给 user
        self.open_id = open_id

    def __str__(self):
        return '%s: %s-%s-%s' % (self.open_id, self.name, self.gender, self.location)


def read_excel(excel_path='/root/workspace/excel/users.xlsx'):
    """
    读 excel 文件
    注意: 到时候写入 fake user 的时候, 在 BaseUserInfo 的 extra_info 里面记录下这是个 fake 的 user --> 先检查下有没有执行过
    :param excel_path:
    :return:
    """
    fake_users = []

    excel_object = xlrd.open_workbook(excel_path)
    table = excel_object.sheets()[0]

    nrows = table.nrows  # 行数
    ncole = table.ncols  # 列数

    fake_open_id = 1

    for i in range(1, nrows):
        row_values = table.row_values(i)
        fake_users.append(
            FakeUser(row_values[0], row_values[1], row_values[2], row_values[3], row_values[4], row_values[5],
                     row_values[6], row_values[7], row_values[8], row_values[9], row_values[10], fake_open_id)
        )
        fake_open_id += 1

    print("user count: ", len(fake_users))
    return fake_users
