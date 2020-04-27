from django.urls import path

from footprint.views import post_footprint_view, comment_footprint_view, get_footprint_detail_view, \
    get_user_footprint_track_view, add_favor_view, user_delete_footprint_view, help_post_pop_up_view, \
    get_user_coupon_list_view

urlpatterns = [
    # 痕迹相关
    path('create/', post_footprint_view),
    path('comment/', comment_footprint_view),
    path('favor/', add_favor_view),
    path('detail/', get_footprint_detail_view),
    path('get_user_track/', get_user_footprint_track_view),

    # zhanghu
    path('user_delete/', user_delete_footprint_view),
    path('user_help_post_pop_up/', help_post_pop_up_view),
    path('user_coupon_list/', get_user_coupon_list_view),
]
