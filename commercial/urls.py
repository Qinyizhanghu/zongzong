from django.urls import path

from commercial.views import get_club_info_view, activity_detail_view, \
    get_top_banner_view, participate_activity_view, get_club_activities_info, favor_activity_view, \
    get_explore_banner_view, get_explore_surplus_times_view

urlpatterns = [
    # @zhanghu
    path('get_top_banner/', get_top_banner_view),
    path('get_explore_banner/', get_explore_banner_view),
    path('get_explore_surplus_times/', get_explore_surplus_times_view),

    path('get_club_info/', get_club_info_view),
    path('get_activity_detail/', activity_detail_view),
    path('subscribe_activity/', participate_activity_view),
    path('get_club_activity_info/', get_club_activities_info),
    path('favor_activity/', favor_activity_view),
]
