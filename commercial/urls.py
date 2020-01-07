from django.urls import path

from commercial.views import get_club_info_view, activity_detail_view, \
    get_top_banner_view  # , participate_activity_view

urlpatterns = [
    path('get_top_banner/', get_top_banner_view),
    path('get_club_info/', get_club_info_view),
    path('get_activity_detail/', activity_detail_view),
    # path('participate_activity/', participate_activity_view),

]