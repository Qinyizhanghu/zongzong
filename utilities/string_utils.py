import random


def random_str(length=8):
    """
    获取一个特定长度的随机串，只包括英文字母和数字
    """
    if length < 1:
        return ''
    return ''.join(random.sample('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', length))


def random_numerical(length=11):
    """
    获取一个特定长度的随机数字串, 且第一位不为 0
    """
    return ''.join(random.sample('123456789', 1)) + ''.join(random.sample('0123456789', length - 1))
