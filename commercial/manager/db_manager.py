from commercial.models import CommercialActivity, Club, ActivityParticipant, ClubCouponTemplate, ClubUserInfo, \
    CouponChargeOffRecord


def get_commercial_activity_by_id_db(activity_id):
    try:
        return CommercialActivity.objects.get(id=activity_id)
    except CommercialActivity.DoesNotExist:
        return None


def get_commercial_activities_by_ids_db(ids):
    return CommercialActivity.objects.filter(id__in=ids)


def get_commercial_activities_by_club_id_db(club_id, start, end):
    return CommercialActivity.objects.filter(club_id=club_id).order_by('-created_time')[start: end]


def get_commercial_activities_by_club(club):
    return CommercialActivity.objects.filter(club=club).order_by('-created_time')


def get_club_by_id_db(club_id):
    try:
        return Club.objects.get(id=club_id)
    except Club.DoesNotExist:
        return None


def get_club_by_account_and_password(account, password):
    try:
        return Club.objects.get(account=account, password=password)
    except Club.DoesNotExist:
        return None


def get_club_user_info_by_user_info_and_club(user_info, club):
    try:
        return ClubUserInfo.objects.get(user_info=user_info, club=club)
    except ClubUserInfo.DoesNotExist:
        return None


def create_club_user_info_by_user_info_and_club(user_info, club):
    return ClubUserInfo.objects.get_or_create(user_info=user_info, club=club)


def get_club_user_info_by_club(club_id):
    return ClubUserInfo.objects.filter(club_id=club_id)


def get_charge_off_record_by_club_user_infos(club_user_infos):
    return CouponChargeOffRecord.objects.filter(club_user__in=club_user_infos).order_by('-created_time')


def get_coupon_template_by_id_db(template_id):
    try:
        return ClubCouponTemplate.objects.get(id=template_id)
    except ClubCouponTemplate.DoesNotExist:
        return None


def get_club_by_ids_db(club_ids):
    return Club.objects.filter(id__in=club_ids)


def create_activity_participate_record_db(activity_id, user_info_id, name, cellphone, num, hint):
    return ActivityParticipant.objects.get_or_create(activity_id=activity_id, user_info_id=user_info_id, defaults={
        'name': name, 'cellphone': cellphone, 'num': num, 'hint': hint
    })


def get_activity_participate_by_activity_and_confirm(commercial_activities, is_confirm):
    return ActivityParticipant.objects.filter(activity__in=commercial_activities, is_confirm=is_confirm)
