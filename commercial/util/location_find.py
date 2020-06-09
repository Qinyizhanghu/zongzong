import requests

from footprint.models import Footprint


"""
地理位置相关: https://zhuanlan.zhihu.com/p/111679535
"""


def location_to_address(location):
    """
    将经纬度转换为地址
    所以选用的是逆地理编码的接口
    :param location: 经纬度，格式为 经度+','+维度，例如:location='116.323294,39.893874'
    :return:返回地址所在区，以及详细地址
    """
    parameters = {
                    'location': location,
                    'key': '0610416f549978a9ce5017dab6195a5a'
                 }
    base = 'http://restapi.amap.com/v3/geocode/regeo?'
    response = requests.get(base, parameters)
    answer = response.json()

    return answer['regeocode']['addressComponent']['district'], answer['regeocode']['formatted_address']


def filling_location_to_footprint():
    """
    给足迹填充 location
    :return:
    """
    footprints = Footprint.objects.filter(id__gte=7519)

    count = 0
    print('has footprint: %s' % len(footprints))

    for footprint in footprints:
        try:
            lon_lat = '%s,%s' % (footprint.lon, footprint.lat)
            location = location_to_address(lon_lat)
            footprint.location = location[1]
            footprint.save()
        except Exception as e:
            print('filling location error: %s' % e)
            continue

        count += 1

        if count % 100 == 0:
            print('processed total footprint %s' % count)
