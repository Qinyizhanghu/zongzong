from django.urls import path

from commercial.views import get_club_info_view, activity_detail_view, \
    get_top_banner_view, participate_activity_view, get_club_activities_info, favor_activity_view, \
    get_explore_banner_view, get_explore_surplus_times_view, get_nearby_clubs_view, club_user_login_view, \
    club_charge_off_user_coupon_view, get_user_coupon_info_for_charge_off_view, club_consume_user_coupon_info_view, \
    club_activity_confirm_info_view

urlpatterns = [
    # @zhanghu
    path('get_top_banner/', get_top_banner_view),
    path('get_explore_banner/', get_explore_banner_view),
    path('get_explore_surplus_times/', get_explore_surplus_times_view),
    path('nearby_clubs/', get_nearby_clubs_view),
    path('user_login/', club_user_login_view),
    path('club_charge_off/', club_charge_off_user_coupon_view),
    path('user_coupon_info_for_charge_off/', get_user_coupon_info_for_charge_off_view),
    path('consume_user_coupon_info/', club_consume_user_coupon_info_view),
    path('activity_confirm_info/', club_activity_confirm_info_view),

    path('get_club_info/', get_club_info_view),
    path('get_activity_detail/', activity_detail_view),
    path('subscribe_activity/', participate_activity_view),
    path('get_club_activity_info/', get_club_activities_info),
    path('favor_activity/', favor_activity_view),
]
