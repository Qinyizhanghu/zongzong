from django.contrib import admin
from reversion.admin import VersionAdmin

from commercial.models import Club, CommercialActivity, TopBanner, ExploreBanner, ClubCouponTemplate


class ClubAdmin(VersionAdmin):
    list_display = ['id', 'name', 'address', 'telephone', 'business_type', 'account', 'password']
    search_fields = ['=id', 'business_type', 'name']


admin.site.register(Club, ClubAdmin)


class ActivityAdmin(VersionAdmin):
    list_display = ['club', 'name', 'address']


admin.site.register(CommercialActivity, ActivityAdmin)


class TopBannerAdmin(VersionAdmin):
    list_display = ['title']


admin.site.register(TopBanner, TopBannerAdmin)


class ExploreBannerAdmin(VersionAdmin):
    list_display = ['title', 'description', 'image', 'is_online']


admin.site.register(ExploreBanner, ExploreBannerAdmin)


class ClubCouponTemplateAdmin(VersionAdmin):
    list_display = ['name', 'type', 'club', 'money', 'threshold', 'count', 'is_online', 'deadline']


admin.site.register(ClubCouponTemplate, ClubCouponTemplateAdmin)
