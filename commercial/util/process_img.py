# -*- coding:utf8 -*-


import ssl
import os
import urllib.request

from commercial.util.stage_1_user_data import read_excel_for_stage_one_user_data


from PIL import Image


"""
对图片进行处理
https://zongz.cn/media/%E9%BB%84.png
https://zongz.cn/media/img_cut/999_6.jpg
"""


def download_img(user_data, file_path):
    """
    下载图片到本地
    :param file_path:
    :param user_data:
    :return:
    """
    for single_data in user_data:
        if not single_data.image_list:
            continue

        fake_id = single_data.fake_id
        sequence = 1

        for img_url in single_data.image_list:
            if 'jpg' not in img_url:
                continue
            try:
                # 是否有这个路径
                if not os.path.exists(file_path):
                    # 创建路径
                    os.makedirs(file_path)
                    # 获得图片后缀
                file_suffix = os.path.splitext(img_url)[1]
                file_name = '%s_%s' % (fake_id, sequence)
                sequence += 1
                # 拼接图片名（包含路径）
                filename = '{}{}{}{}'.format(file_path, os.sep, file_name, file_suffix)
                # 下载图片，并保存到文件夹中
                print(img_url)
                ssl._create_default_https_context = ssl._create_unverified_context
                urllib.request.urlretrieve(img_url, filename=filename)
            except IOError as e:
                print("IOError", e)


def process_source_img(file_dir):
    """
    对原图片做裁剪
    :param file_dir:
    :return:
    """
    img_list = []
    for i, j, k in os.walk(file_dir):
        img_list = k
    print('all image count: %s' % len(img_list))
    target_dir = '/Users/zhanghu05/QinyiZhang/zongzong/img_cut/'

    i = 0
    for img_ in img_list:
        try:
            cut_img(
                file_dir + img_, target_dir + img_
            )
            i += 1
            if i % 100 == 0:
                print('current process %s image!' % i)
        except Exception as e:
            print('-------------------------process error-------------------------', e)


def cut_img(source_file, target_file):
    """
    对图片文件进行裁剪
    :return:
    """
    img = Image.open(source_file)
    print(img.size)
    cropped = img.crop((0, 0, img.size[0], img.size[1] - int(img.size[1] / 10)))  # (left, upper, right, lower)
    cropped.save(target_file)


# download_img(read_excel_for_stage_one_user_data('/Users/zhanghu05/QinyiZhang/zongzong/stage_1_user_data.xlsx'),
#              '/Users/zhanghu05/QinyiZhang/zongzong/img/')

# cut_img('/Users/zhanghu05/QinyiZhang/zongzong/6627_10.jpg', '/Users/zhanghu05/QinyiZhang/zongzong/6627_10_cut.jpg')
# process_source_img('/Users/zhanghu05/QinyiZhang/zongzong/img/')
